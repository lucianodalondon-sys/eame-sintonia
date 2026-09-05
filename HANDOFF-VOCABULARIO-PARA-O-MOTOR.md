# HANDOFF DO VOCABULÁRIO — 38 ISSUE_ID PARA O MOTOR CANÔNICO

Gerado por `scripts/it_vocab_handoff.py`, provado por `scripts/it_vocab_handoff_teste.py`.
Artefacto: `data/samples/IT-ROTULOS-V1/IT-VOCAB-HANDOFF-V1.json`.

> **Isto é um handoff, não uma implantação.** Nenhuma linha do motor foi tocada,
> e nenhuma deve ser tocada a partir daqui.

---

## 1 · Onde está cada coisa

| | |
|---|---|
| Branch atual (coleta e inteligência) | `claude/retomada-coleta-video-convegni-vz50er` |
| Branch onde vive o motor | `claude/opportunity-commercial-priority-v1` |
| Commit lido | `b3935bd03822` |
| Dono único da taxonomia `ISSUE_*` | `scripts/v21_normalizar.py`, dicionário `ISSUE_ALIAS` |
| Quantos IDs ele tem hoje | **24** |

Quem consome o vocabulário, na branch do motor:

`v21_ingest.py` · `v21_ingest_b.py` · `v21_janelas.py` · `v21_comercial.py` ·
`v21_necessidade.py` · `v21_defeitos_do_vinculo.py` · `v21_censo_das_16_janelas.py` ·
`v21_vao_de_janelas.py` · `v21_geografia_contrato.py` ·
`v21_regressao_do_red_team.py` · `tests/test_prioridade_comercial.py`

Todos entram pelas mesmas quatro portas: `issue_id()`, `issues_no_texto()`,
`crop_id()`, `crops_no_texto()`. Nenhum deles lê `ISSUE_ALIAS` directamente.

## 2 · O formato que o motor aceita

```python
ISSUE_ALIAS['ISSUE_<NOME>'] = ['apelido', 'outro apelido', ...]
```

O apelido é **literal**, minúsculo, sem acentos. O motor normaliza os dois lados
com `_n()` — que apaga tudo o que não é `[a-z0-9]` — e casa por **palavra
inteira**, escolhendo sempre **o apelido mais longo**.

Três consequências que não são opinião:

- **Não aceita expressão regular.** Não há lookahead, não há exclusão, não há
  classe de caracteres. Um apelido escrito como regex vira uma frase literal
  impossível.
- **Hífen e apóstrofo são inofensivos.** `collo-cygni` e `dell'olivo`
  normalizam igual dos dois lados.
- **O radical não casa por dentro da palavra.** `thrips` **não** encontra
  `drepanothrips`. Por isso cada género `-thrips` entra como apelido próprio.
  (A camada de rótulos, `scripts/it_rotulo_vocab.py`, usa regex e casa por
  dentro — as duas camadas divergem por desenho, não por erro. Quem comparar
  contagens entre elas vai ver a diferença por esta razão.)

## 3 · O contrato muda? **Não.**

A adição é só de **chaves novas num dicionário existente**. Nenhuma assinatura
de função muda, nenhum ID existente é renomeado ou removido, e nenhum consumidor
precisa de saber que há mais chaves. Um consumidor que hoje recebe `None` para
`'tripidi'` passa a receber `ISSUE_THRIPS` — que é exactamente o efeito pedido.

## 4 · Risco de segundo dono

**Existe, e é a única razão pela qual este ficheiro não é um commit no motor.**

Já há duas listas de vocabulário no repositório:

| camada | ficheiro | forma | escopo |
|---|---|---|---|
| motor | `v21_normalizar.py : ISSUE_ALIAS` | literal + palavra inteira | cruzamento de sinais |
| rótulos | `it_rotulo_vocab.py : ALVOS` | regex | leitura de etiqueta |

Elas convivem porque respondem a perguntas diferentes e ninguém finge que são a
mesma. O que criaria o segundo dono é qualquer uma destas três coisas:

1. editar `v21_normalizar.py` a partir desta branch;
2. fazer cherry-pick do motor para cá para "poder testar";
3. copiar `ISSUE_ALIAS` para dentro de `it_rotulo_vocab.py`.

**Nenhuma foi feita.** O script lê o motor com `git show` e simula a adição em
memória.

## 5 · O que a medição encontrou

Regressão sobre **131 documentos** do acervo italiano, comparando
`issues_no_texto()` antes e depois, frase a frase.

- **38 IDs propostos, 38 implantáveis.**
- **25 ganham ocorrências** no acervo de fala; **13 ficam mudos** — entram pelos
  **rótulos**, que é onde o alvo aparece (`ISSUE_CASSIDA`, `ISSUE_LIXUS`,
  `ISSUE_OULEMA` e companhia vivem na tabela da etiqueta, não no convegno).
- **Nenhum ID existente perde ocorrências.** Zero.

### Incompatibilidade encontrada — uma

`ISSUE_SMUT` trazia o apelido `carbone (?!attiv|medicinal|veget)`. É uma
expressão regular escrita num campo que só aceita literal: `_n()` apagaria os
metacaracteres e o apelido viraria a frase `carbone attiv medicinal veget`, que
não existe em texto nenhum. **Passaria em qualquer regressão por nunca casar
nada** — e é por isso que é um defeito, não uma protecção.

Reparo aplicado aqui, dentro do contrato: o apelido nu `carbone` sai por
completo. Ficam só os inequívocos — `ustilago`, `urocystis`, `carbone volante`,
`carbone della spiga`, `carbone nudo`, `carbone coperto`, `carbone dello stelo`.
O resultado é **mais estreito** do que o proposto, nunca mais largo.

### Sequestro medido — um, e é desejado

`piralide dell olivo` (novo, `ISSUE_OLIVE_PYRALID`) é mais longo do que
`piralide` (existente, `ISSUE_CORN_BORER`). Onde a frase longa aparecer, o ID
novo ganha. Isso está certo — a pirale da oliveira não é a broca do milho — e
**não ocorre uma única vez no acervo actual**, logo o efeito é nulo hoje e
correcto amanhã. Fica declarado para não acontecer por acidente.

### Colisões

Nenhuma. Nenhum apelido novo já pertencia a um dos 24.

## 6 · Ficheiros que precisariam mudar

1. `claude/opportunity-commercial-priority-v1 : scripts/v21_normalizar.py` —
   acrescentar as 38 chaves a `ISSUE_ALIAS`.
2. `claude/opportunity-commercial-priority-v1 : tests/` — o teste mínimo abaixo.

**Só isso.** Nenhum consumidor muda.

## 7 · O teste mínimo, já verde

`scripts/it_vocab_handoff_teste.py` roda contra a cópia em memória do motor e
verifica quatro coisas:

1. cada ID novo que o acervo nomeia **sai de uma frase real**, com `SOURCE_ID`
   ao lado — 25 assertos, nenhuma frase inventada;
2. nenhum ID existente perde o que já reconhecia, salvo o sequestro declarado;
3. nenhum apelido sobrevivente é expressão regular;
4. nenhum apelido tem dois donos.

```
MOTOR       origin/claude/opportunity-commercial-priority-v1 b3935bd03822
IDS ANTES   24
IDS DEPOIS  62
ASSERTOS    25 ancorados em frase real
MUDOS       13 (entram pelos rotulos, nao pelo acervo de fala)
RESULTADO   PASS
```

> Um handoff que não traz o teste já verde é um pedido, não uma entrega.

## 8 · O que entra sem julgamento humano, e o que não

**36 dos 38 entram sem julgamento**: confiança alta na identidade do alvo,
apelidos utilizáveis, zero colisões, zero perdas.

**2 exigem decisão de gente**, e a razão é a mesma nos dois — a identidade do
alvo foi julgada com confiança MÉDIA, não pela mecânica:

- **`ISSUE_NEMATODES`** — o rótulo diz «nematodi» sem dizer quais. Cobrir
  galígenos (*Meloidogyne*), cistícolas (*Globodera*, *Heterodera*) e migradores
  (*Pratylenchus*, *Ditylenchus*, *Xiphinema*) num só ID junta biologias,
  culturas e janelas diferentes. Entra 12 vezes no acervo. Decidir: um ID de
  grupo agora, ou esperar para nascer já com filhos?
- **`ISSUE_OTIORHYNCHUS`** — mudo no acervo de fala, presente só na etiqueta.
  Nada o contradiz; simplesmente não há evidência de fala para o ancorar.

## 9 · Como aplicar com segurança, se e quando for autorizado

A forma comprovadamente segura **não passa por esta branch**:

1. quem detém `claude/opportunity-commercial-priority-v1` abre uma branch a
   partir dela;
2. copia as 38 chaves de `APELIDOS_PROPOSTOS` do artefacto JSON para
   `ISSUE_ALIAS` — é colar, não é traduzir;
3. copia `scripts/it_vocab_handoff_teste.py` para `tests/`, trocando o motor
   simulado pelo `import v21_normalizar` real;
4. roda a suite do motor inteira.

Se em vez disso alguém trouxer o motor para cá, ou levar esta branch para lá, o
resultado é duas listas divergindo em silêncio. **Quem propõe vocabulário não é
quem o implanta.**

## 10 · Os 38, medidos

| ISSUE_ID proposto | termo no rótulo | apelidos que entram | acervo | sem julgamento |
|---|---|---|---|---|
| `ISSUE_ALTERNARIA` | ALTERNARIA | `alternaria`, `alternariosi`, `alternaria solani`, `alternaria mali`, `alternarie` … (6) | 119 | sim |
| `ISSUE_SCALE_INSECTS` | COCCINIGLIE | `cocciniglia`, `cocciniglie`, `cocciniglia farinosa`, `cocciniglie farinose`, `cocciniglia mezzo grano di pepe` … (8) | 63 | sim |
| `ISSUE_WIREWORM` | ELATERIDI | `elateridi`, `elateride`, `elateridae`, `agriotes`, `agriotes sordidus` … (11) | 39 | sim |
| `ISSUE_ANTHRACNOSE` | ANTRACNOSI | `antracnosi`, `antracnosi del noce`, `antracnosi del nocciolo`, `gnomonia juglandis`, `ophiognomonia leptostyla` … (7) | 26 | sim |
| `ISSUE_THRIPS` | TRIPIDI | `tripidi`, `tripide`, `thrips`, `thysanoptera`, `tisanotteri` … (19) | 23 | sim |
| `ISSUE_MEDFLY` | MOSCA | `mosca della frutta`, `mosche della frutta`, `mosca mediterranea della frutta`, `ceratitis capitata`, `ceratitis` … (6) | 19 | sim |
| `ISSUE_ERIOPHYID_MITES` | ERIOFIDI | `eriofidi`, `eriofide`, `eriofide rugginoso`, `acari eriofidi`, `eriophyes` … (10) | 17 | sim |
| `ISSUE_MONILIA` | MONILIA | `monilia`, `monilinia`, `moniliosi`, `moniliose`, `monilosi` … (8) | 16 | sim |
| `ISSUE_PSYLLA` | PSILLE | `psille`, `psilla`, `cacopsylla`, `cacopsylla pyri`, `cacopsylla pyricola` … (9) | 16 | sim |
| `ISSUE_ORIENTAL_FRUIT_MOTH` | CIDIA | `cydia molesta`, `grapholita molesta`, `cidia`, `grafolita`, `tignola orientale del pesco` … (6) | 14 | sim |
| `ISSUE_NEMATODES` | NEMATODI | `nematodi galligeni`, `nematodi fitoparassiti`, `nematodi cisticoli`, `nematodi a cisti`, `meloidogyne` … (12) | 12 | **NÃO** |
| `ISSUE_GALL_MIDGE` | CECIDOMIA | `cecidomia`, `cecidomie`, `cecidomide`, `cecidomidi`, `cecidomiidae` … (14) | 7 | sim |
| `ISSUE_WHITEFLY` | ALEURODIDI | `aleurodidi`, `aleurodide`, `aleurodi`, `aleyrodidae`, `mosca bianca` … (11) | 7 | sim |
| `ISSUE_ANARSIA` | ANARSIA | `anarsia`, `anarsia lineatella`, `anarsia del pesco`, `peach twig borer` | 5 | sim |
| `ISSUE_METCALFA` | METCALFA | `metcalfa`, `metcalfa pruinosa`, `cicalina della melata` | 5 | sim |
| `ISSUE_OLIVE_PYRALID` | MARGARONIA | `margaronia`, `margaronia unionalis`, `palpita unionalis`, `palpita vitrealis`, `glyphodes unionalis` … (7) | 5 | sim |
| `ISSUE_BLACK_ROT` | MARCIUME | `marciume nero`, `marciumi neri`, `guignardia bidwellii`, `phyllosticta ampelicida` | 3 | sim |
| `ISSUE_LEUCOPTERA` | CEMIOSTOMA | `cemiostoma`, `leucoptera scitella`, `leucoptera malifoliella`, `cemiostoma scitella` | 3 | sim |
| `ISSUE_COCKCHAFER` | MAGGIOLINO | `maggiolino`, `maggiolini`, `melolontha`, `melolontha melolontha`, `maggiolino comune` | 2 | sim |
| `ISSUE_PHYLLONORYCTER` | LITOCOLLETE | `litocollete`, `litocollete delle pomacee`, `phyllonorycter`, `phyllonorychter`, `phyllonorycter blancardella` … (9) | 2 | sim |
| `ISSUE_RAMULARIA` | RAMULARIA | `ramularia`, `ramularia collo-cygni`, `collo-cygni`, `ramulariosi` | 2 | sim |
| `ISSUE_AGRILUS` | AGRILO | `agrilo`, `agrili`, `agrilus`, `agrilus viridis`, `agrilo del nocciolo` … (6) | 1 | sim |
| `ISSUE_HELMINTHOSPORIUM` | ELMINTOSPORIOSI | `elmintosporiosi`, `elimintosporiosi`, `helminthosporium`, `helminthosporium gramineum`, `pyrenophora` … (11) | 1 | sim |
| `ISSUE_RHYNCHOSPORIUM` | RINCOSPORIOSI | `rincosporiosi`, `rincosporiose`, `rhynchosporium`, `rhyncosporium`, `rhynchosporium secalis` … (7) | 1 | sim |
| `ISSUE_SAWFLY` | TENTREDINE | `tentredine`, `tentredini`, `tenthredinidae`, `athalia rosae` | 1 | sim |
| `ISSUE_ALFALFA_WEEVIL` | FITONOMO | `fitonomo`, `fitonomi`, `fitonomo dell erba medica`, `hypera postica`, `hypera brunneipennis` … (7) | 0 | sim |
| `ISSUE_APION` | APION | `apion`, `apion pisi`, `holotrichapion pisi` | 0 | sim |
| `ISSUE_BYCTISCUS` | SIGARAIO | `byctiscus`, `byctiscus betulae`, `sigaraio della vite`, `sigaraio` | 0 | sim |
| `ISSUE_CASSIDA` | CASSIDA | `cassida`, `cassida vittata`, `cassida nebulosa`, `cassida della bietola`, `cassida della barbabietola` | 0 | sim |
| `ISSUE_COLORADO_BEETLE` | DORIFORA | `dorifora`, `dorifore`, `dorifora della patata`, `leptinotarsa`, `leptinotarsa decemlineata` | 0 | sim |
| `ISSUE_CONORHYNCHUS` | CLEONO | `cleono`, `cleoni`, `conorhynchus`, `conorhynchus mendicus`, `cleono della barbabietola` … (6) | 0 | sim |
| `ISSUE_HYDRELLIA` | IDRELLIA | `idrellia`, `idrellie`, `hydrellia`, `hydrellia griseola`, `idrellia del riso` | 0 | sim |
| `ISSUE_LIXUS` | LISSO | `lixus`, `lixus spp`, `lixus junci`, `lisso della barbabietola`, `cleono, lisso` | 0 | sim |
| `ISSUE_OTIORHYNCHUS` | OZIORRINCO | `oziorrinco`, `oziorrinchi`, `otiorrinco`, `otiorhynchus`, `otiorhynchus sulcatus` … (6) | 0 | **NÃO** |
| `ISSUE_OULEMA` | LEMA | `oulema`, `oulema melanopus`, `oulema duftschmidi`, `lema melanopus`, `criocera dei cereali` … (6) | 0 | sim |
| `ISSUE_POLLEN_BEETLE` | MELIGETE | `meligete`, `meligeti`, `meligethes`, `meligethes aeneus`, `brassicogethes` … (7) | 0 | sim |
| `ISSUE_SMUT` | CARBONE | `ustilago`, `urocystis`, `carbone volante`, `carbone della spiga`, `carbone nudo` … (7) | 0 | sim |
| `ISSUE_VERTICILLIUM` | VERTICILLIOSI | `verticilliosi`, `verticilliosi dell'olivo`, `tracheoverticilliosi`, `verticillium`, `verticillium dahliae` … (8) | 0 | sim |
