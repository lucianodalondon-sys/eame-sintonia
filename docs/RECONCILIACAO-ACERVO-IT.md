# Por que três leitores do mesmo acervo italiano deram três números

**Missão:** reconciliar `141 / 9.438 / 0` · `101 / 8.770 / 35` · `164 / 29.694 / 82`.
**Resultado:** os três foram reproduzidos **exatamente**. Nenhum estava mentindo.
Estavam medindo coisas diferentes, e a diferença não aparecia em lugar nenhum.

Nada foi escolhido por parecer certo. Cada número abaixo foi rodado.

---

## 1 · As três definições, congeladas

| | **A** · inventário publicado | **B** · script do dono | **C** · leitor independente |
|---|---|---|---|
| **arquivo** | `data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json` | `scripts/it_acervo_inventario_v2.py` | `scripts/passaporte_universos.py` (repo do passaporte) |
| `PATHS` | `data/` inteira | `data/` inteira | **só `data/samples/`** |
| `FILE_TYPES` | `*.json`; erro de leitura → ignorado em silêncio | idem | idem |
| `INCLUSION_RULE` | caminho casa `(^\|/)IT-\|italia\|italy` **ou** doc declara `COUNTRY`/`SOURCE_LOCATION` | idem | **casar com um regex de família** — e pronto |
| `EXCLUSION_RULE` | `data/samples/IT-PORTAL-V1/` + 3 saídas próprias | idem | **nenhuma** |
| `COLLECTION_RULE` | chave de topo → lista não vazia de dicts | idem | idem |
| `RECORD_COUNT_RULE` | sem coleção → **vale 1** (`documento unico`); raiz-lista → `len()` **sem checar tipo** | idem | sem coleção → **0, e o arquivo é descartado**; raiz-lista só se o 1º for dict |
| `UNKNOWN_KEY_RULE` | fora do registro → declara e **reprova** | idem | declara, não reprova |
| `DATE_SCOPE` | nenhum | nenhum | nenhum |
| `COUNTRY_SCOPE` | `IT` por caminho ou documento | idem | **nenhum** — família não é país |
| `DEDUP_RULE` | nenhum | nenhum | nenhum |

> **A e B são o mesmo código.** A é a *saída publicada* dele em 2026-09-04; B é
> ele *rodando hoje*. Que o mesmo código dê 141 e 101 já era o achado.

---

## 2 · Os três números, reproduzidos

`scripts/it_acervo_reconciliar.py` — somente leitura, roda as três regras lado a lado.
`B_POSIX` é B com o caminho normalizado para `/`; `B_NATIVO` é B como ele roda no Windows.

| árvore medida | A publicado | B_NATIVO | B_POSIX | C |
|---|---|---|---|---|
| **`data/` em 2026-09-04** (`git archive 5c2d47f`) | 141 · 9.438 · 0 | 69 · 7.736 · 0 | **141 · 9.438 · 80 · 0** ✅ | 128 · 19.019 · 43 |
| **checkout do passaporte, hoje** | — | **101 · 8.770 · 35** ✅ | 220 · 18.615 · 93 | **164 · 29.694 · 82** ✅ |
| **este checkout, hoje** | — | 79 · 7.976 · 13 | 184 · 17.702 · 51 | 159 · 29.617 · 79 |

Três batidas exatas, nas quatro dimensões cada uma. Os três números têm dono:

- **141** = a regra de B, com caminho POSIX, sobre a árvore de 4 de setembro.
- **101** = a regra de B, com caminho Windows, sobre o checkout do passaporte.
- **164** = a regra de C, sobre o checkout do passaporte.

---

## 3 · Diff de pertença — 247 arquivos vistos por alguém

Sobre **uma só** árvore (este checkout), para separar diferença de regra de
diferença de árvore. `A` aqui é a regra de A aplicada hoje (`B_POSIX`).

| balde | arquivos |
|---|---:|
| `ALL_AGREE` | 57 |
| `A_ONLY` | 66 |
| `C_ONLY` | 62 |
| `A_C_ONLY` | 40 |
| `A_B_ONLY` | 21 |
| `B_ONLY` | 1 |
| `B_C_ONLY` | 0 |

**Por que C recusa 87 arquivos que A aceita:**

| motivo | arquivos |
|---|---:|
| `ZERO_REGISTOS_DESCARTA_FICHEIRO` — documento agregado, C joga fora | **45** |
| `SEM_FAMILIA` — nenhum regex casou | 37 |
| `FORA_DE_data_samples` | 5 |

**Por que A recusa 62 arquivos que C aceita:**

| motivo | arquivos | registros |
|---|---:|---:|
| não passa no teste de Itália de A | 55 | **17.361** |
| camada de método `IT-PORTAL-V1` | 7 | 185 |

**`B_ONLY` tem exatamente um arquivo:** `data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V1.json`
— a camada de método que só B inclui, porque no Windows a exclusão não funciona.
Um arquivo, e prova sozinho a causa nº 1.

---

## 4 · As causas — cada uma medida, nenhuma suposta

### 4.1 `WRONG_PATH` — a barra invertida · 141 → 69 na mesma árvore

B escreve as regras com `/` literal:

```python
re.search(r'(^|/)IT-|italia|italy', caminho)      # o teste de Itália
any(('/%s/' % d) in (base + '/') for d in CAMADA_DE_METODO)   # a exclusão
```

No Windows, `os.path.relpath` devolve `data\samples\IT-CAMPO-V1\x.json`. Não há
`/` nenhum. **As duas regras deixam de casar ao mesmo tempo:** arquivos italianos
aninhados param de entrar, e a camada de método para de ser excluída.

Medido na árvore de 4 de setembro: **141 com `/`, 69 com `\`**. Mesmo código,
mesmos dados, dois sistemas operacionais.

### 4.2 `STALE_OWNER` — a árvore cresceu · 141 → 184 → 220

Mesma regra (`B_POSIX`), três árvores:

```
2026-09-04, quando A foi declarado    251 json em data/    141 arquivos
este checkout, hoje                   410 json em data/    184 arquivos
checkout do passaporte, hoje          447 json em data/    220 arquivos
```

Os dois checkouts **não têm os mesmos dados**: o passaporte tem 37 arquivos a
mais, entre eles `IT-CASOS/` inteiro (16 arquivos) e 4 de `IT-FONTES/`.
Comparar um número medido num com um número medido no outro compara duas coisas.

### 4.3 `COLLECTION_FILTER` — família não é país · 17.361 registros

C decide pertença por **casar com um regex de família**. Sete desses regexes não
nomeiam país nenhum: `nuts2`, `RESEARCHER`, `SPEAKER`, `COMPETITOR`, `MARKET`,
`PRICES`, `ECONOMIC`, `TERRITORIAL`, `SENSOR-PILOT`, `EARLY_SIGNAL`.

Os maiores arquivos que **só C** conta:

| registros | arquivo | o que é |
|---:|---|---|
| 5.685 | `EU-T1-001-nuts2-crop-area.json` | Eurostat NUTS2, `SOURCE_LOCATION = EUROPEAN UNION`, nota do próprio arquivo: *"apenas FR/ES/IT"* |
| 4.759 | `SENSOR-PILOT/MEDICAO.json` | `ORIGINAL_LANGUAGE = pt`, `FACT_LOCATION = ver por item` |
| 775 | `RESEARCHER-CORPUS-EAME-V1.json` | corpus EAME inteiro |

**Os 29.694 não são um acervo italiano.** São uma contagem por assunto que varre
dado francês, espanhol, brasileiro e da EAME para dentro do total da Itália.
Esta é a maior causa isolada da diferença de registros.

### 4.4 `DUPLICATE_COUNT` invertido — o documento agregado que some · 45 arquivos

B: arquivo sem lista nenhuma vale **1** (`documento unico`) — decisão explícita e
escrita do dono. C: vale **0** e o arquivo **sai do universo**.

Não é preferência de contagem: são 45 arquivos italianos que desaparecem de um
dos leitores sem deixar rastro.

### 4.5 `GENERATED_FILE_INCLUDED` — 7 arquivos, 185 registros

C não exclui `data/samples/IT-PORTAL-V1/`, a camada onde vivem contratos,
handoffs e o próprio inventário. Nas palavras do dono: *"o acervo é o que
medimos; o contrato é como o medimos. Um contador que soma os dois não está a
medir: está a aplaudir-se."*

### 4.6 `BUG` latente — lista de raiz sem checar o tipo

B conta `len(lista)` numa lista de raiz **sem verificar se os elementos são
dicionários**. Hoje isso não morde (medido: 2 arquivos de raiz-lista, ambos de
dicionários), mas uma lista de mil textos viraria mil registros. A regra
canônica fecha a porta antes de alguém passar por ela.

### 4.7 O erro de instrumento — o medidor que escreve

`it_acervo_inventario_v2.py` **regrava o artefato que mede**. Rodá-lo para
conferir se o dono ainda bate destrói o dono. Já aconteceu uma vez, foi detectado
por `git status` e revertido. Aqui ele **não foi executado**: as regras dele
foram reimplementadas em modo leitura, e há teste que cai se essa escrita sumir
sem alguém reavaliar o aviso.

---

## 5 · A regra canônica

Escrita em `docs/UNIVERSO-ACERVO-IT-REGRA-CANONICA.md`, derivada do **significado**
do universo — o acervo italiano é *o que medimos sobre a Itália* —, não do número
que se queria ver.

O que ela muda em relação às três:

| decisão | por quê |
|---|---|
| todo caminho comparado com `/`, em qualquer sistema | uma regra que muda de resultado com o SO não é uma regra |
| país é declarado por **caminho**, `COUNTRY` ou `FACT_LOCATION` — nunca por família | família diz do que trata, nunca de onde é |
| `SOURCE_LOCATION` **não** entra | fonte não é assunto: 6 arquivos de `IT-MERCADO` vêm do Eurostat e falam da Itália |
| documento agregado vale 1, com chave própria | 45 arquivos sumiam calados |
| lista de raiz só conta se os elementos forem dicionários | fecha o bug latente |
| `data/runs/` fora | é `UNIVERSE_EXECUCOES`, universo declarado à parte — somar é duplicar |
| `data/samples/IT-PORTAL-V1/` fora | é a papelada sobre o acervo, não o acervo |
| `.json` que não abre **reprova** | hoje são 0; engolir a exceção transforma corrupção em número menor |
| `FILE_LIST` obrigatória na saída | A publicou totais e nunca guardou **quais** arquivos contou — por isso sua pertença teve de ser reconstruída, não lida |

---

## 6 · Convergência

Dois leitores, sem uma linha de classificação em comum. A é procedural
(`os.walk`, predicados nomeados, segmentos partidos à mão); B é `pathlib.rglob`
com tabela de decisão e contagem por compreensão. Nenhum importa o outro — há
teste que verifica isso.

```
                      LEITOR A     LEITOR B
FILES                      178          178
RECORDS                 17.612       17.612
COLLECTIONS                116          116
UNKNOWN_KEYS                51           51
FINGERPRINT   ca4ceca25cd4762ba91f69ba360349cf313f7724ce02e613d274d72d0acf3f91
                                        (idêntica)

INDEPENDENT_READERS_AGREE = SIM
CANONICAL_RULE_PROVED     = SIM
```

Concordam também em `FILE_LIST`, `PER_KEY` e `PER_FAMILY`, arquivo a arquivo e
chave a chave — não só nos totais.

### Mas o acervo ainda não passa no portão

```
ACERVO_PASSA_NO_PORTAO       = NAO
MOTIVO                       = UNKNOWN_COLLECTION_KEY = 51
UNIVERSE_ACERVO_IT_CANONICAL = NAO
```

São **37 chaves distintas**, em 51 lugares, carregando **7.512 registros** —
`data` (2.730), `PARES` (2.146), `REGISTROS` (641), `produtos` (602), `ITENS`,
`CREATORS`, `SUBSTANCIAS`… Todas parecem coleções legítimas.

**Não as adicionei ao registro.** A lei do próprio registro diz:

> *"Uma chave nova não entra aqui sozinha: o inventário reprova e alguém decide
> se é coleção ou não."*

Esse alguém não é quem está medindo. A reprovação é o portão funcionando, não
falhando.

---

## 7 · O estado proposto para o dono — **não aplicado**

```
ARQUIVO = data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json
ESTADO  = INTACTO (md5 640531c6… igual ao do início da missão)
```

| campo | `OLD` | `PROPOSED` | `WHY_CHANGED` |
|---|---:|---:|---|
| `FICHEIROS` | 141 | 178 | árvore cresceu (251→410 json) + caminho POSIX + país por declaração |
| `TOTAL_REAL_ACERVO` | 9.438 | 17.612 | mesmos motivos; nenhum registro novo foi inventado |
| `CHAVES_DE_COLECAO_ENCONTRADAS` | 80 | 116 | 36 formas de coleção que o registro nunca viu |
| `CHAVES_NAO_RECONHECIDAS` | 0 | **51** | ← **é isto que trava a atualização** |
| `CAPTURED_AT` | 2026-09-04 | data da decisão | — |
| `FINGERPRINT` | não declarava | `ca4ceca2…` | dimensão nova: dono sem digital não é auditável |
| `FILE_LIST` | não declarava | 178 caminhos | dono sem lista de membros não é auditável |

Por família:

| família | `OLD` | `PROPOSED` | nota |
|---|---:|---:|---|
| `ROTULOS_PORTFOLIO` | 6.249 | 8.622 | |
| **`OUTROS`** | 23 | **5.418** | `IT-ARPAV-VENETO`, `IT-T4-001`, `IT-V2`, `IT-LASTMILE` — dado italiano legítimo que a tabela de famílias não cobre |
| `SINAIS_DE_CAMPO` | 640 | 1.048 | |
| `MERCADO` | 1 | 78 | |
| `HANDOFF_METODO` | 94 | 16 | a papelada saiu, como a lei do dono manda |
| `SENSORES_HUMANOS` | 4 | 0 | `SENSOR-PILOT` é EAME, não italiano |
| `RADAR_FUTURO` · `FITOSSANITARIO` · `FONTES` · `OPORTUNIDADES` · `SOCIAL_INSTAGRAM` · `CONCORRENCIA` | 622 · 560 · 317 · 609 · 315 · 4 | 625 · 560 · 317 · 609 · 315 · 4 | praticamente estáveis |

**O que falta para aplicar, e é decisão sua:**

1. As **37 chaves novas** são coleções? Se sim, o registro é re-semeado e o
   `UNKNOWN` cai a 0. Se alguma não for, ela precisa de outro destino.
2. `OUTROS` com 5.418 registros diz que a **tabela de famílias está velha**.
   Ela é sua; não mexi. Vale uma família para `IT-ARPAV-VENETO` e outra para
   `IT-T4-001`/`IT-V2`?
3. O passaporte cobra `UNIVERSE_ACERVO_IT` contra o dono. Enquanto o dono não for
   atualizado, aquele portão continua `FAIL` — e continua **certo** em falhar.

---

## 8 · O que foi tocado

```
CRIADOS   docs/UNIVERSO-ACERVO-IT-REGRA-CANONICA.md
          docs/RECONCILIACAO-ACERVO-IT.md
          scripts/it_acervo_reconciliar.py      as três regras lado a lado
          scripts/it_acervo_leitor_a.py         leitor canônico A
          scripts/it_acervo_leitor_b.py         leitor canônico B
          scripts/it_acervo_convergencia.py     o portão
          tests/test_it_acervo_canonico.py      21 testes

ALTERADOS nenhum
data/     INTACTO — git status data/ vazio; md5 dos dois artefatos do dono
          idêntico ao do início da missão
passaporte  NÃO TOCADO (lido para achar a origem dos números, nunca escrito)
portal      NÃO TOCADO
deploy      NÃO
```

Como rodar:

```bash
py -3 scripts/it_acervo_convergencia.py --raiz .
py -3 -m unittest tests.test_it_acervo_canonico
py -3 scripts/it_acervo_reconciliar.py --raiz . --diff
```
