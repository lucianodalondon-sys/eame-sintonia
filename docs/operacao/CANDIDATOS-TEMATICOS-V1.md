# CANDIDATOS TEMÁTICOS — V1

> **Isto define e congela. Não mede.** Nenhum candidato foi executado,
> nenhum viu o corpus de avaliação, nenhum venceu.
> ```
> CANDIDATE_SET_VERSION    = V1
> CANDIDATE_SET_SHA256     = 3fda8edc39ecedbbb9314f195a697d131b7cab8ca24c3dec16aaac41116988a4
> FROZEN_BEFORE_EVALUATION = YES
> BENCHMARK_EXECUTED       = NO
> ```
> **Os números e as fichas vivem no código.** O dono é
> `provas/candidatos_tematicos.py`; este documento explica e cita, e um
> teste prova que os dois dizem o mesmo.

> **Missão:** `C-DEFINE-CANDIDATOS-TEMATICOS-V1`

---

## 1 · A ORDEM É A MISSÃO INTEIRA

Um candidato desenhado depois de ver onde o corpus aperta não é um
candidato: é uma resposta decorada com cara de hipótese.

```
A HIPÓTESE VEM PRIMEIRO, E FICA ESCRITA.
DEPOIS MEDE-SE. NUNCA AO CONTRÁRIO.
```

O fingerprint existe para isso: qualquer alteração posterior muda o hash,
e um hash que mudou depois da medição é uma confissão.

---

## 2 · O QUE FOI MEDIDO, E MUDOU O CONTRATO DE ENTRADA

### Só `texto` carrega conteúdo

A porta actual lê seis campos. No caminho do documento, **apenas `texto`**
é povoado — `title`, `nome`, `topics`, `crops` e `resumo` são lidos pela
regra de hoje e escritos por ninguém.

### O caminho carrega a classe declarada

```
78 de 78 identificadores de fonte do atlas embutem o token do universo
```

`IT-T3-002` diz «fonte 002 do território T3». E o caminho do ficheiro
embute o identificador. Logo:

```
ENTREGA-SE OS BYTES AO CANDIDATO. NUNCA O CAMINHO.
```

Proibidos como feature, por medição e não por política: `source_id`,
`CONTENT_PATH`, `BODY_PATH`, `CANONICAL_PATH`, `ALL_PATHS`, `ITEM_ID`.

A fonte fica como **contexto e estrato de avaliação**, nunca como decisão.
O contraexemplo canónico desta casa é a ARPAV: uma mesma instituição
publica material de universos diferentes. Externamente é o caso do
classificador de cavalos que lia a marca da fonte na imagem
([Lapuschkin et al., *Nature Communications* 10:1096, 2019](https://www.nature.com/articles/s41467-019-08987-4)).

### Não há corpus de treino independente

As únicas duas origens que servem de gabarito são o gabarito de T2
(universo errado) e o próprio conjunto de avaliação. O livro de decisões
tem 813 itens e nasceu das palavras de hoje.

```
UM CLASSIFICADOR TREINADO NAS RESPOSTAS DO ANTERIOR
NÃO O SUBSTITUI: CONFIRMA-O.
```

---

## 3 · OS QUATRO CANDIDATOS

| id | família | determinismo | treino | API externa | estado |
|---|---|---|---|---|---|
| `C1-LEXICAL-STRUCTURED` | LEXICAL_RULE | YES | NO | NO | DEFINED_NOT_IMPLEMENTED |
| `C2-TAXONOMY-CONCEPT` | TAXONOMY_ONTOLOGY | YES | NO | YES | EXISTING_COMPONENT_REUSABLE |
| `C3-LLM-STRUCTURED` | LANGUAGE_MODEL | NO | NO | YES | DEFINED_NOT_IMPLEMENTED |
| `C4-HYBRID-CASCADE` | HYBRID_CASCADE | PARTIAL | NO | YES | DEFINED_NOT_IMPLEMENTED |

### `C1-LEXICAL-STRUCTURED` · Regra lexical estruturada

**Hipótese.** O que falha hoje e o CASAMENTO, nao o inventario. Trocando correspondencia por posicao de caracteres por fronteira de palavra (Unicode UAX #29), acrescentando escopo de negacao (NegEx/ConText) e peso por evidencia, a mesma lista de hoje decide melhor.
ESTE CANDIDATO E O CONTROLO: ele isola UMA variavel. Se ele subir muito, o defeito era o mecanismo; se nao subir, o defeito esta no inventario, e nenhuma lista escrita a mao o conserta.

**Força esperada.** Deterministico, sem dependencia externa, explicavel ao nivel do trecho que disparou. Mata por construcao o defeito de substring que a baseline mediu.

**Fraqueza esperada.** O inventario continua escrito a mao, e ha prova externa de que isso e fragil: King, Lam & Roberts (AJPS 2017) pediram a 43 pessoas a lista de termos de um tema com exemplos a vista — mediana de 8 termos, 149 termos unicos no total, e em 66% deles NENHUMA das outras 42 pessoas se lembrou do mesmo. Duas listas diferentes produzem conjuntos diferentes.

**O que o invalidaria.** Se ele empatar com o mecanismo actual, a hipotese cai: o defeito nao era o casamento, e melhorar o casamento nao resolve.

```
abstenção YES · explicabilidade ALTA — a decisao E a regra que disparou
falha     sem regra acima do limiar -> NAO_SEI
parâmetros congelados: limiar_de_peso, janela_de_escopo
CANDIDATE_SPEC_SHA256 = 93722187b51d3bf2772b2312d6ff871e37873cc45455543ae83db90e7ab8981c
```

Fontes: [1](http://www.unicode.org/reports/tr29/) · [2](https://www.sciencedirect.com/science/article/pii/S1532046409000744) · [3](https://gking.harvard.edu/files/ajps12291_final.pdf)

### `C2-TAXONOMY-CONCEPT` · Taxonomia controlada com evidencia lexical

**Hipótese.** O alvo da decisao nao e a palavra: e o CONCEITO. Um vocabulario controlado ja existente da o inventario que ninguem desta casa consegue recordar, e da-o em varias linguas de uma vez — porque o conceito e neutro e as etiquetas e que sao por lingua.
Esta arvore JA TEM metade do material: `coleta/eppo_gd.py` le nomes por codigo EPPO (italiano incluido) e o dicionario local tem 1381 codigos de alvo e 492 de cultura, com nome cientifico.

**Força esperada.** Zero dados rotulados, deterministico, multilingue por construcao e explicavel ate ao conceito. O indexador oficial da UE (JEX) mede F1 0.48-0.54 em 22 linguas com parametros por omissao e conclui que o algoritmo e «nearly language-independent» — raro, e directamente util ao problema de idioma nao resolvido desta casa.

**Fraqueza esperada.** Cobertura do vocabulario, e ela JA ESTA MEDIDA nesta arvore: o dicionario local veio de tabelas espanholas e generos so italianos passam sem conferencia (`Scaphoideus` nao esta nele). E o JEX documenta o outro buraco: texto institucional repetitivo polui a evidencia lexical e precisou de lista de paragem multi-palavra.

**O que o invalidaria.** Se a cobertura do vocabulario no corpus real for baixa ao ponto de a abstencao estourar o limite de cobertura do gate.

```
abstenção YES · explicabilidade ALTA — «etiqueta X do conceito C, que de
falha     vocabulario indisponivel -> ERRO, nunca NAO. E se nenhum conceito passa o limiar -> NAO_SEI
parâmetros congelados: limiar_de_conceitos, profundidade_hierarquia
CANDIDATE_SPEC_SHA256 = 2a443e1b731d2f8b41c1911f6e717d0b14c0783821493c6493022653121b532e
```

Fontes: [1](https://www.w3.org/TR/skos-reference/) · [2](https://aims.fao.org/standards/AGROVOC/concept-scheme) · [3](https://arxiv.org/pdf/1309.5223) · [4](https://github.com/NatLibFi/Annif/wiki/Backend:-MLLM)

### `C3-LLM-STRUCTURED` · Modelo de linguagem com saida estruturada

**Hipótese.** A decisao e de LEITURA, e nao de casamento. Um modelo que le o documento inteiro distingue «menciona» de «trata de» — que e exactamente onde a baseline falhou — e nao precisa de artefacto por lingua nem de deteccao de idioma.
A saida e forcada ao vocabulario da porta por esquema, para o candidato nao poder inventar um estado que a porta nao tem.

**Força esperada.** Le o documento em vez de o procurar. Nao precisa de inventario escrito a mao, e por isso escapa ao defeito que King, Lam & Roberts mediram. Melhor das quatro familias para idioma nao resolvido ou misturado.

**Fraqueza esperada.** NAO E DETERMINISTICO, e nem sequer a temperatura zero: a causa documentada e a dependencia do tamanho do lote nos nucleos de reducao do servidor, que varia com carga alheia. Por isso `k_amostras` e parametro congelado — a saida trata-se como distribuicao, nao como valor.
E ha vies de seleccao medido: modelos preferem certos identificadores de opcao (Zheng et al., ICLR 2024, 20 modelos), o que faz da ORDEM das opcoes um hiperparametro — por isso ela tambem esta congelada.

**O que o invalidaria.** Se k amostras da mesma entrada divergirem acima do que o gate tolera, ou se a abstencao so aparecer quando o prompt a sugere — ha prova de que a taxa de abstencao pode medir a redaccao do prompt e nao a incerteza do modelo.

```
abstenção YES · explicabilidade APARENTE, e essa e a armadilha. Da para 
falha     API indisponivel, tempo esgotado ou saida invalida -> ERRO. NUNCA NAO, NUNCA NAO_SEI: uma falha de execucao nao e uma opiniao, e o gate conta-as em caixas diferentes.
parâmetros congelados: k_amostras, ordem_das_opcoes, modelo_fixado
CANDIDATE_SPEC_SHA256 = 8f25566b855892f7ab284d786f3e5ad1b14b71d05778a379b761ee5ba7997a73
```

Fontes: [1](https://developers.openai.com/api/docs/guides/structured-outputs) · [2](https://arxiv.org/abs/2309.03882) · [3](https://arxiv.org/abs/2506.09038) · [4](https://aclanthology.org/2024.emnlp-industry.91/) · [5](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)

### `C4-HYBRID-CASCADE` · Cascata: conceito primeiro, leitura depois

**Hipótese.** As fraquezas de C2 e C3 sao COMPLEMENTARES, e uma cascata cobre-as: o conceito decide o que consegue decidir — deterministico, barato, explicavel — e so o que sobra paga a leitura.
A propriedade auditavel que so esta familia da: «tantos por cento dos documentos foram decididos por regra deterministica». Isso e uma medida de confianca que nenhuma das outras produz.

**Força esperada.** A fraccao decidida pelo primeiro andar e deterministica, gratuita e explicavel; o custo por documento so incide no resto. Arquitectura documentada em producao: os ensembles do Annif correm nas bibliotecas nacionais finlandesa, alema e polaca.

**Fraqueza esperada.** Depende do sinal de escalada estar calibrado, e e ai que ela herda o pior dos dois andares. Nao encontrei fonte primaria que isole um modo de falha caracteristico de cascatas — a literatura publica os sucessos. Isso e uma lacuna, e fica escrita como lacuna, nao como seguranca.

**O que o invalidaria.** Se a fraccao resolvida deterministicamente for pequena, a cascata e C3 com um passo a mais e o custo nao se justifica.

```
abstenção YES · explicabilidade ALTA ao nivel do sistema, porque o regis
falha     segundo andar indisponivel -> o que foi escalado sai ERRO, e o que o primeiro andar ja tinha resolvido MANTEM-SE. Degradacao parcial, nao queda total.
parâmetros congelados: limiar_de_escalada, ordem_dos_andares
CANDIDATE_SPEC_SHA256 = 6576de74800139c9c7b2ec983ff074b883cd1a4cd912c2442ef896926e7632fc
```

Fontes: [1](https://arxiv.org/abs/2305.05176) · [2](https://github.com/NatLibFi/Annif/wiki/Backend:-nn_ensemble) · [3](https://arxiv.org/abs/1711.10160)

---

## 4 · AS DUAS FAMÍLIAS QUE FICARAM DE FORA

```
UMA EXCLUSÃO MEDIDA VALE MAIS DO QUE UM QUINTO CANDIDATO DE ENFEITE.
```

### SUPERVISED_CLASSIFIER — `BLOCKED_PENDING_INDEPENDENT_TRAINING_SET`

MEDIDO nesta arvore: nao existe corpus de treino de T3 independente. As unicas duas origens que servem de gabarito sao o gabarito de T2 (universo errado) e o proprio conjunto de avaliacao, ja declarado EVALUATION. O livro de decisoes tem 813 itens e nasceu das palavras de hoje — treinar nele ensinaria o substituto a repetir o mecanismo que ele substitui.
E os 36 NAO se partem em treino e teste: ja foram declarados avaliacao, e parti-los seria fabricar independencia.

**O que desbloqueia.** Um conjunto rotulado por pessoa, independente dos 36. A literatura da a ordem de grandeza: com 8 exemplos por classe o desvio-padrao entre 10 particoes e de ~5 pontos — abaixo disso a diferenca entre dois candidatos e menor do que a diferenca entre duas particoes do mesmo.

### DENSE_EMBEDDING — `DEFERRED`

Nao e falta de merito — e que o proximo passo dela seria um acto de contaminacao. Um classificador por semelhanca precisa de um PROTOTIPO, e a unica definicao canonica escrita de T3 nesta arvore tem quatro palavras. Escrever um prototipo mais rico AGORA, tendo eu ja visto o corpus numa missao anterior, seria escrever a resposta e chamar-lhe hipotese.
A alternativa limpa — embeber as etiquetas do vocabulario controlado — usa a MESMA fonte de evidencia que C2 e transforma-se numa variacao dele, nao numa familia nova.
Ha ainda duas medicoes externas contra a pressa: nenhum modelo de embedding domina todas as tarefas (MTEB, 58 conjuntos, 112 linguas), logo a ESCOLHA DO MODELO passaria a ser ela propria um benchmark dentro do benchmark; e o espaco vectorial codifica IDENTIDADE DE LINGUA e nao so significado, o que num corpus de idioma nao resolvido e um erro de encaminhamento silencioso.

**O que desbloqueia.** Um prototipo cuja origem seja anterior ao conjunto de avaliacao e um codificador fixado em arvore, com busca exacta.

---

## 5 · A ABSTENÇÃO É UMA CAMADA, NÃO UM CANDIDATO

Ela **embrulha** qualquer um dos quatro sem os modificar. Pô-la a concorrer
seria comparar um mecanismo com um acessório.

O que ela oferece: garantia de amostra finita sem suposicao de distribuicao, e — na variante de controlo de risco — a possibilidade de fixar a TAXA DE FALSO NEGATIVO como alvo, que e exactamente o lado caro do custo assimetrico deste gate

O que exige: um conjunto de calibracao separado do treino E do teste. A ordem de grandeza publicada: ~1000 para a maioria dos casos, 102 para folga de 0.05. NAO pode ser os 36.

**A armadilha, registada:** a cobertura e MARGINAL, nao condicional: da para ter 90% no total e zero num estrato. E ha prova de que a abstencao pode AUMENTAR a disparidade entre grupos, porque o mecanismo abstem-se onde ja acertava. Medir por universo e por lingua, nunca so no agregado.

---

## 6 · O QUE O ESTUDO EXTERNO NÃO FECHOU

- nenhuma fonte primaria isola um modo de falha caracteristico de cascatas
- nenhuma fonte primaria quantifica a precisao POR LINGUA de classificacao por modelo de linguagem com saida estruturada — a vantagem multilingue de C3 e plausivel por arquitectura e NAO medida
- nenhuma fonte primaria estabelece que a justificacao gerada por um modelo seja FIEL a decisao que ele tomou
- nenhuma fonte primaria mede a transicao especifica desta casa (lista plana de substring -> qualquer outra coisa) em documentos institucionais

Ficam escritas como lacunas, não como segurança.

---

## 7 · A EXPOSIÇÃO PRÉVIA DE QUEM DESENHOU

```
DESIGNER_PRIOR_EXPOSURE = YES
```

numa missao anterior da MESMA sessao, quem desenhou estas fichas correu a baseline e viu a saida POR DOCUMENTO, os termos que acenderam e quais itens eram falso positivo.

**Por que está escrito.** nao da para desver, e fingir que da seria a propria contaminacao. Declarar e a unica mitigacao honesta.

**Mitigação estrutural.** nenhuma ficha pode ENUMERAR termos da regra actual nos campos de configuracao, nem citar publicador, ITEM_ID ou SHA. O validador recusa a ficha que o fizer, e ha teste que prova que ele recusa.

**O que isto não resolve.** a escolha das FAMILIAS pode ter sido informada por saber onde o mecanismo actual falha. Isso e mitigado pelas fontes: as quatro familias vem do estudo externo e nao do corpus.

---

## 8 · O QUE ESTA MISSÃO NÃO FEZ

```
BENCHMARK_EXECUTED = NO      CANDIDATE_RESULTS_VIEWED = NO
ADMISSION_CHANGED  = NO      GATE_THRESHOLD_CHANGED   = NO
```

O mecanismo actual **não é candidato**. Ele entra depois como
`BASELINE / CONTROL`, e fica intacto — corrigi-lo agora destruiria a
comparação.

```
EVALUATION_SCOPE = ITALIAN_AGRO_INSTITUTIONAL_CORPUS
```

Não autoriza França, Espanha nem EAME.
