# `UNIVERSE_ACERVO_IT` — a regra canônica

**Estado:** especificação. Dois leitores independentes a implementam sem partilhar
uma linha de classificação. Enquanto os dois não derem o mesmo número em todas as
cinco dimensões, `UNIVERSE_ACERVO_IT_CANONICAL = NÃO`.

Este documento é a **fonte**. Os leitores são traduções dele. Se um leitor e este
texto discordarem, o texto está certo e o leitor tem um defeito.

---

## 0 · A pergunta que este universo responde

> **Quais coleções e arquivos pertencem ao acervo italiano canônico?**

Acervo é **o que medimos sobre a Itália**. Não é o que *dizemos* sobre o que medimos
(contratos, verificações, handoffs, o próprio inventário), e não é o *registro de
quem rodou o quê* — esse é `UNIVERSE_EXECUCOES`, um universo declarado à parte, e
somar os dois produz um total que não é total de nada.

Três frases do próprio dono, que esta regra preserva inteiras:

- *"uma coleção é qualquer chave de topo cujo valor seja lista não vazia de dicionários"* — a **forma**, não uma lista branca de nomes.
- *"o acervo é o que medimos; o contrato é como o medimos. Um contador que soma os dois não está a medir: está a aplaudir-se."*
- *"um total que encolhe em silêncio é pior que um total que falha: o segundo alguém conserta."*

---

## 1 · `CANONICAL_INCLUSION_RULE`

Um arquivo pertence ao universo quando **as quatro** condições valem:

### 1.1 `PATHS`
Está sob `data/`, em qualquer profundidade, a partir da raiz do repositório.

### 1.2 `FILE_TYPES`
O nome termina em `.json` (minúsculas) **e** o conteúdo é JSON válido em UTF-8.

> Um `.json` que não abre **não é ignorado**. Entra em `ILEGIVEL`, e a corrida
> **REPROVA**. Um leitor que engole a exceção transforma corrupção em um número
> menor, e um número menor parece um número.

### 1.3 `COUNTRY_SCOPE` — o teste de Itália
Vale se **qualquer uma** for verdadeira:

| # | teste | o que é |
|---|---|---|
| `PATH` | algum segmento do caminho, depois de `data/`, é `IT`, começa por `IT-`, ou contém `ITALIA`/`ITALY` (sem distinguir maiúsculas) | curadoria declarada: alguém pôs o arquivo numa gaveta italiana |
| `COUNTRY` | o documento é um dicionário e `COUNTRY` ou `country` ∈ {`IT`, `ITALY`, `ITALIA`} | o próprio documento se declara |
| `FACT_LOCATION` | o documento é um dicionário e `FACT_LOCATION` casa com `ITAL` | o **fato** é sobre a Itália |

**O que explicitamente NÃO torna um arquivo italiano:**

- casar com um padrão de família que não nomeia país — `nuts2`, `RESEARCHER`,
  `SPEAKER`, `COMPETITOR`, `MARKET`, `PRICES`, `ECONOMIC`, `TERRITORIAL`,
  `SENSOR-PILOT`, `EARLY_SIGNAL`. Família diz **do que trata**, nunca **de onde é**.
- `SOURCE_LOCATION`. **Fonte não é assunto.** Seis arquivos de `IT-MERCADO`
  declaram `SOURCE_LOCATION = EUROPEAN UNION` e `FACT_LOCATION = PAIS - Italia`:
  vêm do Eurostat, falam da Itália. Excluir por fonte derrubaria dado italiano real.

### 1.4 `EXCLUSION_RULE`
Fica **fora** quem satisfaz qualquer uma:

| chave | o quê | por quê |
|---|---|---|
| `CAMADA_DE_METODO` | qualquer caminho que passe por `data/samples/IT-PORTAL-V1/` | é o que dizemos sobre o acervo, não o acervo. Sem isto o total sobe sempre que alguém escreve um contrato. |
| `UNIVERSO_EXECUCOES` | qualquer caminho que passe por `data/runs/` | universo declarado à parte, com dono próprio (`scripts/proveniencia.py`). Somar é duplicar. |
| `SAIDA_DE_LEITOR` | os arquivos que os próprios leitores gravam | um contador não se conta a si próprio. Ficam fora de `data/` por construção; a regra é redundante de propósito. |

---

## 2 · `COLLECTION_RULE` — a forma

Depois de ler o documento:

| caso | chave gerada | registros |
|---|---|---|
| dicionário, chave de topo `K` cujo valor é lista não vazia cujo **primeiro elemento é um dicionário** | `K` | `len(lista)` |
| a raiz é uma lista não vazia cujo **primeiro elemento é um dicionário** | `__RAIZ__` | `len(lista)` |
| a raiz é uma lista **vazia**, ou lista cujo primeiro elemento não é dicionário | `__VAZIO__` | `0` |
| dicionário sem nenhuma chave que satisfaça a linha 1 | `__DOCUMENTO_UNICO__` | `1` |

Duas decisões que separam esta regra das três anteriores, e a razão de cada uma:

- **O teste de dicionário vale também na raiz.** O script do dono conta
  `len(lista)` numa lista de raiz **sem verificar o tipo dos elementos** — uma
  lista de mil textos viraria mil registros. Hoje isso não acontece em nenhum
  arquivo (medido: 2 arquivos de raiz-lista, ambos de dicionários), mas a regra
  fecha a porta antes de alguém passar por ela.
- **Documento agregado vale 1, e não desaparece.** O leitor independente devolve
  zero registros e **descarta o arquivo inteiro do universo**: 45 arquivos
  italianos somem por aí. Um documento agregado é um registro. Vale 1, com chave
  reservada própria, e aparece na contagem.

---

## 3 · `RECORD_COUNT_RULE`

`RECORDS` = soma dos registros de todas as chaves de todos os arquivos incluídos.

**Invariante permanente:** a soma por família tem de ser igual à soma por chave.
Um registro que exista no total e não caia em família nenhuma desaparece sem
destino, e é assim que um acervo encolhe sem ninguém dar por isso.

---

## 4 · `UNKNOWN_KEY_RULE`

Toda chave de coleção tem de constar do registro
`data/samples/IT-PORTAL-V1/IT-ACERVO-CHAVES-V1.json`, semeado a partir do próprio
acervo e nunca inventado.

Chave fora do registro → entra em `UNKNOWN_COLLECTION_KEY` **com nome, arquivo e
número de registros**, e a corrida **REPROVA**. Nunca conta como 1 em silêncio.

As três chaves reservadas — `__RAIZ__`, `__VAZIO__`, `__DOCUMENTO_UNICO__` — são
da regra, não do acervo, e não são cobradas ao registro.

---

## 5 · `DEDUP_RULE`

Um arquivo é contado **uma vez**, identificado pelo caminho relativo à raiz do
repositório com `/` como separador.

Não há deduplicação por conteúdo: dois arquivos com bytes idênticos em caminhos
diferentes são dois arquivos. Deduplicar por conteúdo esconderia cópia acidental,
que é exatamente o que se quer ver.

---

## 6 · `DATE_SCOPE`

Nenhum. O universo é a árvore **no estado em que está**. Não há corte por data, e
`CAPTURED_AT` de um arquivo não o inclui nem o exclui.

A árvore é fixada pela impressão digital, não por uma data.

---

## 7 · `FINGERPRINT`

```
para cada arquivo incluído, ordenado pelo caminho relativo em ordem de byte:
    h.update(caminho_relativo_posix.encode('utf-8'))
    h.update(b'\n')
    h.update(sha256(bytes_do_arquivo).hexdigest().encode('utf-8'))
    h.update(b'\n')
FINGERPRINT = h.hexdigest()          # sha256
```

Depende do conjunto de arquivos **e** do conteúdo de cada um. Dois leitores que
concordam em quantidade e discordam em quais arquivos dão digitais diferentes —
é para isso que ela existe.

---

## 8 · O separador de caminho

Toda comparação de caminho — segmento, exclusão, regex — é feita sobre o caminho
**normalizado para `/`**, em qualquer sistema operacional.

Não é detalhe de estilo. O script do dono escreve `(^|/)IT-` e `/IT-PORTAL-V1/`;
no Windows `os.path.relpath` devolve `\`, nenhuma das duas regras casa, e o mesmo
código sobre a mesma árvore devolve **141 num sistema e 69 no outro**. Uma regra
que muda de resultado com o sistema operacional não é uma regra.

---

## 9 · Saída obrigatória

Os dois leitores devolvem, com estes nomes exatos:

```
FILES · RECORDS · COLLECTIONS · UNKNOWN_KEYS · FINGERPRINT
FILE_LIST                    caminhos incluídos, ordenados
PER_KEY                      chave de coleção -> registros
PER_FAMILY                   família -> registros
UNKNOWN_COLLECTION_KEY       [{CHAVE, FICHEIRO, REGISTOS}]
ILEGIVEL                     [{FICHEIRO, ERRO}]
INVARIANT_FAMILY_SUM_OK      bool
```

`FILE_LIST` é obrigatória. O inventário publicado guardou totais e **nunca guardou
quais arquivos contou** — por isso a sua pertença não pôde ser diferenciada
arquivo a arquivo, só reconstruída. Um dono sem lista de membros não é auditável.
