# RELATÓRIO — MISSÃO L1 · GATE MULTILÍNGUE DA ADMISSION

Branch `multilingue-v1`, a partir de `origin/unificacao-v1` (`2cfdc3b3`). Motor: `claude-opus-5-5`.

```
COLLECTION NÃO CORREU · NADA NA SALA · BANCO NÃO TOCADO · SERVIÇOS VIVOS NÃO TOCADOS
Writeset: admissao/admissao.py, admissao/idioma.py (novo), tests/ (2 novos), este relatório, know-how
Nenhum limiar mudou: SINAIS_MINIMOS = 2; NAO só com prova de outro universo
```

---

## 0 — O QUE JÁ EXISTIA

* `admissao/admissao.py:593` já tinha a receita da casa: *«não se traduz a lista:
  junta-se a outra língua ao lado»* — por isso as listas têm IT e PT.
* Detecção de idioma na régua: **nenhuma**. A Bíblia só fala de idioma a propósito
  do lugar do fato (`leis/lugar_do_fato.py`, «independente de idioma»).
* Juntar o inglês ao lado **não serve**: `export` saiu de T10 porque casava nos
  blocos «potrebbe interessarti» de páginas **italianas**. O inglês ao lado traria
  esse ruído de volta e mudaria vereditos italianos (proibido).

---

## 1 — CAPACIDADE REAL: QUE LÍNGUAS O CONTEÚDO TRAZ

`py admissao/idioma.py <pastas>` — palavras-função por língua, decide só com
**≥ 20** sinais e **≥ 1,5×** a segunda língua; senão NAO_SEI.

| corpus | it | en | pt / fr / es / de | não sei |
|---|---|---|---|---|
| lote-76 (76 textos derivados) | 65 | **10** | 0 | 1 |
| gabarito do detector (168 págs.) | 126 | 8 | 0 | 34 |
| gabaritos T2/T12 V2 + V3 + CATALOGO-PROVA (207) | 178 | 0 | 0 | 29 |
| páginas das receitas e da coorte (56) | 45 | 1 | 0 | 10 |
| **total (507)** | **414** | **19** | **0** | **74** |

```
IDIOMAS_MEDIDOS = it 414 · en 19 · pt 0 · fr 0 · es 0 · de 0 · não sei 74 (páginas vazias/JS ou curtas)
SUPORTE_REAL    = it, pt (já existiam) + en (esta missão). fr/es/de: IDIOMA_NAO_SUPORTADO — dito, não fingido.
```

Os 10 ingleses do lote-76 são **exactamente os 10 da Zootecnica** (121–317
palavras-função inglesas, 0–1 italianas). O «não sei» é uma notícia italiana
curta (19 sinais < 20): fica com a régua de sempre.

---

## 2 — A CORRECÇÃO (mínima, sem afrouxar)

**A mesma régua, na língua do texto:**

```
língua do texto   lista usada                                   limiares
it / pt / NAO_SEI PERGUNTAS_DO_UNIVERSO — exactamente como antes  iguais
en                PERGUNTAS_EN — os MESMOS conceitos, em inglês   iguais
fr / es / de      NAO_SEI  «IDIOMA_NAO_SUPORTADO:<xx>»            —
```

Cada termo inglês é equivalente de um termo IT/PT **que já estava** na lista
(T3, T4, T5, T7, T9, T10). Ficaram **de fora**, declarado, as armadilhas de
substring do mesmo tipo das que já limparam o italiano: `trial` (indus**trial**),
`event` (pr**event**), `product` (**product**ion), `thesis` (syn**thesis**),
`import` (**import**ant), `pest` (**pest**icide, Buda**pest**), `trap`
(s**trap**); e os equivalentes de `listino`/`rincar`/`borsa merci` (cabem dentro
de `price`/`commodity` e dariam dois sinais a uma palavra). `resistance` não
entra: o italiano não tem `resistenza` na lista. Nenhuma forma cabe dentro de
outra da mesma lista (prova).

---

## 3 — PROVA SEM AFROUXAR

### Lote-76, re-medido OFFLINE (`tests/medir_multilingue.py`)

Régua ANTES = `2cfdc3b3:admissao/admissao.py` (git show, em memória); DEPOIS =
árvore. 76 documentos × {T10 (a pergunta com que foram escritos), universo da
fonte} = **132 pares**.

```
MUDARAM 6 de 132 — TODOS ingleses, TODOS em T10, TODOS a partir de NAO_SEI
```

| derived | o que é | antes | depois | porquê |
|---|---|---|---|---|
| 845 | Indonésia exporta frango (**gabarito item 6**) | NAO_SEI | **SIM** | price, exports |
| 850 | Produção de frango na UE, preços em queda (**gabarito item 5**) | NAO_SEI | **SIM** | price, imports, exports |
| 851 | Indonésia pede adiamento de subida de preços das rações | NAO_SEI | **SIM** | price, imports, exports |
| 846 | Memorando FEFAC–Sindirações (rações UE–Brasil) | NAO_SEI | **SIM** | imports, exports ⚠️ |
| 844 | Doença de Newcastle em explorações húngaras | NAO_SEI | **NAO** | prova de outro universo (T5, T9) |
| 852 | Obituário (**gabarito item 7**) | NAO_SEI | **NAO** | prova de outro universo (T5 research, university) |

Os outros 4 ingleses (843, 847, 848, 849) ficam **NAO_SEI**: só uma palavra de
mercado cada, e uma palavra solta não chega (limiar 2, intacto).

```
IT_VERDICTS_CHANGED = 0 (65 textos italianos + 1 de língua incerta, nas duas perguntas)
SIM_TO_NAO          = 0
NAO_TO_SIM (italiano) = 0
```

⚠️ **846** não está no gabarito. No meu diagnóstico de 22/09 era «mercado
lateral, NÃO SEI» (acordo sectorial com comércio de rações). Agora é SIM por
`imports` + `exports`. Pode merecer olhar humano.

### Gabarito dos 10 (validado pelo dono)

| item | antes | depois | esperado |
|---|---|---|---|
| 5 (850) | NAO_SEI | **SIM** | ENTRA ✅ |
| 6 (845) | NAO_SEI | **SIM** | ENTRA ✅ |
| 7 (852) | NAO_SEI | **NAO** | NÃO ENTRA ✅ — **mudou**, na direcção do gabarito |
| 1, 2, 3, 4, 8, 9, 10 | — | **iguais** | (italianos: nada muda por construção) |

⚠️ O briefing pedia «os outros 8 mantêm o veredicto». **7 mantêm; o item 7 mudou
de NAO_SEI para NAO** — que é exactamente o esperado do gabarito. Declaro-o em vez
de o esconder.

### Controlo negativo

| texto | T10 (mercado) | nota |
|---|---|---|
| marketing inglês (lançamento, campanha, feira, prémios) | **NAO** | D8: marketing recusado ✅ · em T9 (concorrência/marketing) dá SIM, como a régua italiana com «campagna, lancio, novità, fiera» |
| obituário, doença animal, prémio, regras ambientais (EN reais) | **nunca SIM** | ✅ |
| artigos científicos ingleses (Bulletin of Insectology, Phytopathologia) | NAO | SIM em T5 (e T3 no de fitopatologia) — certo |
| ⚠️ páginas de CAPA inglesas (ex.: índice da Zootecnica) | SIM | acendem vários universos, **como as capas italianas**: dezenas de títulos. Separar capa de notícia é do detector de capa, não desta régua |

```
NEGATIVE_CONTROL = PASS (marketing e fora-do-tema em inglês nunca SIM em mercado)
```

---

## 4 — TESTES E REGRESSÃO

`tests/test_admissao_multilingue.py` — **13 provas**, sem rede: itens 5 e 6
entram · fora do tema e marketing nunca SIM em T10 · o limiar não muda (um sinal
= NAO_SEI) · NAO só com prova de outro universo · italiano com palavras inglesas
no menu usa a régua italiana · italiano de mercado continua SIM pela lista
italiana · língua duvidosa = régua de sempre · frase inglesa curta (abaixo do
mínimo) = régua de sempre · texto meio-meio = língua NÃO SEI · francês =
`IDIOMA_NAO_SUPORTADO:fr` · a lista inglesa só tem universos que já têm régua ·
nenhuma forma dentro de outra · as armadilhas medidas ficaram de fora.

**Regressão** — os 34 módulos de `tests/` que usam a régua, **964 testes**,
comparados **por nome** com a base (`2cfdc3b3`, numa cópia de trabalho à parte,
uma medição de cada vez):

```
BASE   : 116 falhas + 6 erros (a suíte já chega vermelha nesta máquina)
AGORA  : 118 falhas + 6 erros
NOVAS  : 2 — test_candidatos_tematicos…test_a_admissao_e_o_gate_nao_mudaram
             test_gate_de_aceitacao_tematica…test_a_admission_nao_foi_tocada
         ambas medem `git diff HEAD` em admissao/ (mudança POR COMMITAR): depois do
         commit, 2/2 OK. Não são regressões.
PERDIDAS: 0
```

⚠️ `BASELINE_CONGELADO` (a guarda dos 36 documentos T3) **passa**, mas confere um
artefacto guardado — não volta a julgar os documentos, e os textos deles não
estão no repositório. Não o conto como prova do italiano; a prova é a
re-medição do lote-76.

### Mutação (Python Mutation Law: cache limpa, `PYTHONDONTWRITEBYTECODE=1`, processo novo, execução provada por ficheiro-marca)

| mutante | executou | resultado |
|---|---|---|
| tirar o vocabulário inglês de mercado (itens 5/6 voltam a NAO_SEI) | sim | morto |
| desligar a escolha de língua | sim | morto |
| francês passa calado | sim | morto |
| lista inglesa também no italiano | sim | morto |
| mínimo do detector a zero | sim | **sobreviveu** → prova nova → morto |
| margem do detector a 1,0 | sim | morto |

```
MUTATION = 6/6 mortos (1 depois de acrescentar a prova que faltava)
```

---

## ENTREGA

```
IDIOMAS_MEDIDOS            = it 414 · en 19 · pt/fr/es/de 0 · não sei 74  (507 ficheiros)
SUPORTE_REAL               = it, pt, en · fr/es/de = IDIOMA_NAO_SUPORTADO (explícito)
GABARITO_10                = itens 5 e 6 NAO_SEI → SIM · item 7 NAO_SEI → NAO (= esperado) · 7 iguais
LOTE76                     = 6/132 pares mudam, todos ingleses em T10: 4 NAO_SEI→SIM, 2 NAO_SEI→NAO
IT_VERDICTS_CHANGED        = 0
SIM_TO_NAO                 = 0
NEGATIVE_CONTROL           = PASS
MUTATION                   = 6/6
TESTS                      = 13/13 novos · regressão 964: 0 novas falhas depois do commit
MULTILINGUAL_GATE_PROVEN   = YES — para inglês, a única língua estrangeira que o conteúdo real traz.
                             fr/es/de: NAO_SEI dito, sem suporte fingido.
```

---

## EM PALAVRAS SIMPLES

A porta da Sala decide se uma notícia serve, procurando palavras-chave. Só
conhecia palavras em **italiano** e **português**. Quando chegava uma notícia em
**inglês**, não encontrava nada e dizia "não sei" — mesmo quando a notícia era
exactamente sobre preços e exportações. Você decidiu (D3) que a língua sozinha
não pode dar "não sei".

O que fiz: agora a porta **vê primeiro em que língua** está a notícia e usa a
lista de palavras **dessa língua**. Para o inglês, escrevi os mesmos conceitos
que já existiam em italiano, deixando de fora as palavras-armadilha (por exemplo,
"trial" aparece dentro de "industrial").

A régua não ficou mais fácil: continua a exigir **duas palavras** do assunto,
como antes.

**O que mudou de verdade**, nas 76 notícias do lote:

- **4 notícias inglesas de mercado passaram a entrar**, entre elas as duas do
  frango que você disse que deviam entrar;
- **2 notícias inglesas passaram a "não"**, por serem de outro assunto (um
  obituário e uma doença de animais);
- **nenhuma notícia italiana mudou.**

Notícias em francês, espanhol ou alemão dão agora "não sei" **com o motivo
escrito** ("língua não suportada"). No conteúdo que temos não apareceu nenhuma,
por isso não fingi saber ler essas línguas.
