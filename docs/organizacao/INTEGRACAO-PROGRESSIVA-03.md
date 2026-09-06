# P0.2 · PASSO 03 — O ENXERTO ITALIANO, E AS TRÊS COISAS QUE ELE OBRIGOU A CORRIGIR

Continuação de `INTEGRACAO-PROGRESSIVA-02.md`. Uma ref, medida e integrada — e três
decisões de coordenação que só apareceram **porque** a ref foi medida a sério.

---

## 1. Cabeçalho

| Campo | Valor |
|---|---|
| `HEAD_BEFORE` | `bdb57cf` |
| `SELECTED_REF` | `claude/sintonia-italy-pilot-b1l401` |
| `SELECTED_REF_HEAD` | `b929879` (2026-08-30) |
| `MERGE_BASE` | `9693399` |
| `HEAD_AFTER` | `0226813` (merge `69db7cc` + as correcções das duas revisões) |
| `MERGE_ATTEMPTED` | SIM — `git merge --no-ff`, dois pais reais |
| `MERGE_VERDICT` | **PASS** |
| `P0_2_STEP_03` | **PASS** — publicado; ver §1.1 |

### 1.1 · O estado que este documento tinha declarado, e que ainda não era verdade

Este cabeçalho dizia `P0_2_STEP_03 = PASS` enquanto:

```
PUSH_EXECUTED          = NÃO   nenhum remoto contém 69db7cc
REMOTE_CANONICAL_HEAD  = bdb57cf   (inalterado)
WORKTREE_STATUS        = 57 caminhos modificados — as correcções do red team
                         ainda não estão no commit
REVISORES              = 3 workflows a correr sobre essas mesmas correcções
```

**Um ledger que declara PASS antes de o portão fechar é exactamente o defeito que este
passo passou o dia a corrigir noutros ficheiros.** `DOCUMENTO_DECLARA != REPOSITÓRIO_TEM`.
O estado passou a `IN_FLIGHT` e só foi a `PASS` quando as três condições ficaram medidas e
verdadeiras ao mesmo tempo. Ficaram:

```
REVISORES              3 workflows terminados, 18 agentes cada; 3 blockers contra
                       correcções da primeira ronda, todos reproduzidos e fechados
CORRECÇÕES             commit 0226813, 58 ficheiros, árvore limpa
FETCH ANTES DO PUSH    origin/sintonia/canonical = bdb57cf — sem drift
PUSH                   bdb57cf..0226813, fast-forward, sem force
REMOTE DEPOIS          origin/sintonia/canonical = 0226813
```

A linha `PASS` acima só existe porque estas cinco medições existem. Esta secção fica como
está: o estado errado que o documento chegou a declarar é registo, e apagá-lo faria a régua
parecer sempre certa.


54 commits entraram na linhagem com história preservada. Sem squash, sem rebase, sem
cherry-pick, sem cópia de ficheiro, sem force.

> **Nada foi herdado.** Nenhum ranking, conflito, portão ou teste medido contra `15b1ec2`,
> `70b097e`, `aac90ad` ou `3f01544` entrou aqui. Tudo o que está abaixo foi medido contra
> `bdb57cf`.

---

## 2. As três decisões, e por que existem

A ref não era um enxerto neutro: ela trazia **leitura**. E leitura que entra por enxerto
pode rebaixar leitura que já passou portão. As três decisões existem para impedir isso.

### 2.1 · `fato_local.py` — a ref não é autoridade semântica por trazer 90 testes

A ref trazia `tests/test_fato_local.py` com 90 testes e uma versão de `scripts/fato_local.py`.
Quatro dessas leituras já tinham sido refutadas nesta casa. As cinco leis ficam de pé:

```
EVENTO                != FATO
LOCAL_DA_FONTE        != LOCAL_DO_FATO
SEDE                  != LOCAL_DO_FATO
RISK_WORD             != PHYTOSANITARY_RISK
GENERIC_PRESENCE      != DISEASE_PRESENCE
```

Quatro correcções cirúrgicas, todas provadas por execução contra contraexemplos
reproduzidos do próprio repositório:

| # | Onde | O que mudou | Por quê |
|---|---|---|---|
| C1 | `_governa()` | âncora negativa que **precede** o lugar só desqualifica quando **nada positivo se intromete** entre ela e o lugar | a primeira versão da regra também matava *«Convegno a Bologna e fusariosi constatata a Grosseto»* |
| C2 | `localizacoes_do_fato()` | a primeira frase só é **cabeçalho** se ela própria **não relata** | um cabeçalho que relata um facto não pode ser descartado como moldura |
| C3 | vocabulário | cai a alternativa `di` de `presenz[ae]\s+(?:…\|di)` | `GENERIC_PRESENCE != DISEASE_PRESENCE`: *«presenza di»* sozinho não é presença de doença |
| C4 | vocabulário | `rischio` passa a exigir **sujeito de risco**, nunca artigo | `RISK_WORD != PHYTOSANITARY_RISK`: *«rischio per la salute»* não é risco fitossanitário |

**Resultado medido: os 90 testes da ref passam.** Nenhum precisou ser classificado como
`LEGACY_REF_EXPECTATION / SEMANTICALLY_REJECTED` — a divergência era do código, não do teste.
As seis cicatrizes viraram teste próprio em `tests/test_cicatrizes_do_leitor_italiano.py`
(14 provas), com os contraexemplos reproduzidos, incluindo uma string real de
`SENSOR-PILOT/VIDEOS-A.json`.

### 2.2 · Cobertura de rótulo — uma régua que media outra coisa

`LABEL_COVERAGE: 163/163 (100%)` com `PARSE_FAILURES = 0`, enquanto **40** produtos saíam
sem uma cultura e sem um alvo. Ninguém mentiu: o número media **download** e era lido como
**leitura**, e ninguém dizia qual. Passa a haver seis estágios, separados por obrigação:

| estágio | medido | o que mede |
|---|---|---|
| `LABEL_DISCOVERY_COVERAGE` | **163/163** | rótulos que se **tentou alcançar** (`ATTEMPTED`), contra os que o registo declara |
| `LABEL_DOWNLOAD_COVERAGE` | **163/163** | PDF baixado, sha256 conferido |
| `TEXT_EXTRACTION_COVERAGE` | **163/163** | ficheiros com ≥ 1.000 bytes **contados no disco**, em `IT-ROTULOS-V1/testo/` |
| `LABEL_READ_COVERAGE` | **123/163** | ao menos uma cultura **OU** um alvo — e o que o vocabulário **fechado de 17 termos** alcança |
| `CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE` | **96/163** | alguma cultura **E** algum alvo, em qualquer parte do texto |
| `MODE_OF_ACTION_DECLARED_COVERAGE` | **70/163** | grupo de acção declarado |

E, **fora da escada**, porque é outro leitor e não outro degrau:

| | medido | |
|---|---|---|
| `COBERTURA_DO_LEITOR_CANONICO` | **128/163** | rótulos com par no `IT-ROTULOS-PARES-V3`, com `UNIVERSOS_BATEM` conferido |

**Três nomes mentiam, e a revisão adversarial mostrou-o.** `AUTHORIZED_USE_ROW_COVERAGE`
usava um termo que **já tem dono nesta casa e vale 19** — cultura, alvo e dose na MESMA
linha da tabela —, e chamar 96 à conjunção de duas presenças inflava o termo em 5×.
`LABEL_DISCOVERY_COVERAGE` era `OBTAINED := TARGET`: um degrau **incapaz de ficar abaixo de
100 %** para qualquer entrada, e era justamente o degrau em que se confia para dizer «achámos
todos». `USE_ROWS_STRUCTURED_COVERAGE` vinha depois de `READ = 123` e lia-se como o degrau
seguinte, mas **128 > 123**: 31 dos 40 que este artefacto não leu estão dentro dos 128.

```
PARSER_FAILURE   != ABSENCE
ZERO_PARSED_ROWS != ZERO_AUTHORIZED_USES
```

Os 40 mudos ficam `READ/STRUCTURING_DEBT`, e **nunca** `REGULATORY_ABSENCE` — mas a dívida
partiu-se em dois baldes, porque «nunca do rótulo» generalizava uma prova que só cobre 31:

```
CONFIRMED_PARSER_DEBT   38   31 porque o leitor canónico leu par no MESMO rótulo
                              7 porque o vocabulário DESTA casa acha a cultura no texto
                                arquivado, fora de contexto de rotação
UNCONFIRMED_SILENCE      2   009783 · cita `agrumi`, cultura fora dos 17 termos → dívida
                                      de VOCABULÁRIO
                             017852 · coadjuvante declarado, não tem cultura própria →
                                      o silêncio é do documento
```

`UNCONFIRMED_SILENCE != DEBT != ABSENCE`. Ter o texto no repositório prova que o texto
existe, não que o rótulo declara uso.

**E a primeira versão desta divisão errava em 8 dos 9, na direcção lisonjeira — outra vez
minha, outra vez apanhada por revisão adversarial.** Eu perguntava só ao leitor canónico e
mandava para `NAO SEI` tudo o que ele não tivesse visto. O texto arquivado respondia:
`015630` tem uma secção literal `COLTURE AUTORIZZATE` com
`VITE (da vino e da tavola) / Contro peronospora (Plasmopara viticola): impiegare 270 g/ha`
— uma linha de uso autorizado completa, o padrão-ouro desta casa —, `017580` e `017983` são
`DISERBANTE SELETTIVO PER LA BARBABIETOLA DA ZUCCHERO`, e em cinco dos oito a cultura está
**dentro** do vocabulário fechado de 17 termos. Não era dívida de vocabulário: era dívida
pura de leitura, exactamente como os 31.

Antes chamava-se ausência ao silêncio; depois chamei «não sei» a uma dívida medida. As duas
direcções mentem, e a segunda mente sobre um ficheiro que o próprio bloco cita como prova.

    NAO SEI SOBRE FICHEIRO QUE TEMOS EM DISCO = NÃO TER OLHADO

Agora a dívida tem **duas provas independentes e basta uma**, e cada um dos dois `NAO SEI`
que restam traz a sua razão **medida** no texto, não redigida.

**`COM_TEXTO_INTEGRAL_NO_REPO` deixou de ser `len(ids)`.** Era igual a `COUNT` por
construção, logo incapaz de discordar de si mesmo: esvaziar os 40 ficheiros de texto não
reprovava nada. Agora vem do disco, com piso de bytes. E `JA_LIDOS` deixou de ser pertença
**negativa** (`r not in sem_par`), que dava por lido pelo canónico qualquer registo que o
canónico nunca tivesse visto.

**A lei mora no GERADOR, não só no ficheiro gerado.** `scripts/italia_portfolio.py` passou a
derivar os seis estágios e a dívida; uma correcção que vivesse só no artefacto seria apagada
na execução seguinte. `tests/test_cobertura_de_rotulo.py` (15 provas) exige que gerador e
artefacto concordem campo a campo.

**Achado lateral, medido:** a afirmação publicada *«nenhum dos 163 rótulos nomeia
Bactrocera oleae»* estava apoiada na leitura parcial. Foi reconferida no **texto integral
dos 163**: sobrevive. Três rótulos citam o **género** `Bactrocera` — e os três são
`Bactrocera dorsalis`, mosca-da-fruta em pomar. `GENUS_MATCH != SPECIES_MATCH`, e uma busca
por género teria "refutado" uma afirmação correcta.

### 2.3 · Leitor canónico de rótulos = `IT-ROTULOS-PARES-V3`

A ref trazia um leitor de **30/08/2026** com **90 pares**, que declarava como limitação
intransponível *«o dicionário é espanhol, Scaphoideus não está nele»*. A casa já tinha, de
**04/09/2026**, `IT-ROTULOS-PARES-V3`: **2.928 pares**, `it_rotulo_parser/3.4.0`, portão
`IT-ROTULOS-PORTAO-V1 = PASS` contra gabarito de 30 rótulos lido à mão — e que resolve
exactamente aquela limitação.

```
OLDER_SMALLER_READER            != CANONICAL_READER
NEW_MERGE_CANNOT_DOWNGRADE_GATED_READING
```

O artefacto da ref fica `LEGACY_READER / HISTORICAL_INPUT`, `CANONICAL_AUTHORITY = NO`.
O bloco inteiro passou a ser **derivado** por `scripts/italia_reg_intelligence.py`, e não
escrito à mão no JSON — escrito à mão, desaparecia na primeira regeneração e o
`LABEL_COVERAGE: 163/163 (100%)` voltava com ele.

**Três números estavam errados, e a revisão adversarial provou-o:**

```
ANTES   SUBSUMED_BY_IT_ROTULOS_PARES_V3 = PARCIAL — 37 de 49   (12 não cobertas)
DEPOIS  CROP_PRESENTE_NO_CANONICO       = 39 de 49   (10 não cobertas)
        USE_ROWS_COM_ALVO_REPRODUZIDO   = 0 de 217 triplas
```

O 37 vinha de comparar `FRUMENTO TENERO` com `FRUMENTO` por igualdade literal e chamar
lacuna à **mesma linha do rótulo** que o canónico tinha lido; o substantivo-cabeça resolve, e
`018067` e `019095` passam para o lado coberto. E «37 de 49» lia-se como *usos reproduzidos*
quando é **cultura, e só cultura**: o canónico publica CLASSE de alvo (`AFIDI`, `INFESTANTI`)
e o legado publica ESPÉCIE (`Aphis pomi`), e **nenhum** dos 217 alvos do legado aparece como
alvo do canónico. Ler o número como usos preservados apagaria a espécie julgando-a preservada.

**Das 10 não cobertas, 4 são defeito conhecido do legado, não lacuna do canónico.** `Riso`
foi lido de dentro do nome de uma erva daninha — `Riso crodo)` — em quatro herbicidas de
glifosato **não selectivo**; a auditoria da casa já o tinha provado. Ficam
`KNOWN_DEFECT / DO_NOT_REPROCESS`: o canónico está **certo** em não os ter, e enfileirá-los
para reprocessamento seria pedir de volta uma linha que oferece glifosato a uma lavoura de
arroz. Sobram **6 lacunas reais**, em dois rótulos.

**A comparação de tamanho também mudou de régua.** «2.928 contra 90» compara
`(registo, cultura, classe)` com `(cultura, espécie)` — e a própria casa já tinha escrito que
«somar os dois seria comparar réguas diferentes». A conclusão sobrevive na régua honesta:
**128 rótulos com par contra 19**.

Os **7** campos que só o legado tem (`DOSES`, `INTERVAL_DAYS`, `MAX_APPLICATIONS`,
`EVIDENCE`, `ROW_STATE`, `CROP_TERM_MATCHED`, `REGULATORY_CATEGORY`) entram como
`CANDIDATE_INPUT_TO_CANONICAL_READER` — **nunca como autoridade**.

`tests/test_leitor_canonico_de_rotulos.py` passou de 10 para 22 provas e deixou de contar
para passar a **recomputar**: o conjunto das não cobertas é refeito dos dois ficheiros em vez
de se aceitar o comprimento da lista, o portão `IT-ROTULOS-PORTAO-V1` é **aberto** e cada
check é conferido em vez de citado, e a varredura documental exige que **todo** documento que
cite «90 pares» nomeie o leitor canónico — antes, uma errata que invertia a decisão passava,
porque as três palavras que o teste procurava estavam lá.

---

## 3. Fontes — dado não entra órfão de fonte documentada

Sete fichas entram. Quatro portadas da ref (`IT-T4-001-ETICHETTA`, `IT-T1-001`, `IT-T3-006`,
`IT-T3-LOTTA-OBBLIGATORIA`) e **três escritas agora**, porque o enxerto trouxe dado que
dependia delas:

- **`IT-T3-002`** — Servizio fitosanitario da Regione del Veneto. Já era **perna de caso
  publicado** (`IT-HERO-001` e `IT-DEMO-001`), com conteúdo citado e datado, e não tinha
  ficha. Fichada contra os PDFs preservados em `data/samples/IT-ARPAV-VENETO/`. Ressalva de
  dono registada: o mesmo directório guarda o boletim **agrometeorológico da ARPAV** —
  `AGROMETEO != FITOSANITARIO`.
- **`IT-T3-LAMMA`** — Consorzio LaMMA (Toscana/CNR). HTML preservado, 25.680 bytes, sha256
  reconferível. Defeito da fonte medido: **página rolante, série FORWARD-ONLY**.
- **`IT-T3-OP`** — organizações de produtores olivícolas. `YELLOW`, uma de quatro lida.
  Lei acrescentada: `SOURCE_LAYER != SIGNAL_ABSENCE`.

**`IT-T1-001` sai de `NÃO SEI` para `GREEN`** — e a linha da rodada em que não foi alcançada
**fica**, marcada como resolvida. `NOT_REACHED != DOES NOT EXIST`, e a prova é a linha ter
mudado de estado sem ser removida.

### 3.1 · O placar, recontado

```
ANTES   37 SOURCE_IDs · 26 fichas · 16 GREEN · 4 YELLOW · 0 RED · 17 NÃO SEI
DEPOIS  40 SOURCE_IDs · 34 fichas · 20 GREEN · 4 YELLOW · 0 RED · 16 NÃO SEI
ITALY   de 1/2/0/3 = 6  para  5/2/0/2 = 9
```

Três IDs movem a contagem: `IT-T3-002`, `IT-T3-006` e `IT-T5-001`. **`IT-T5-001` entrou por
simetria, e a assimetria era o defeito:** `ES-T5-002` — o recorte **espanhol** da mesma fonte
(OpenAlex), pela mesma rota — sempre foi ficha, SOURCE_ID contado e um dos GREEN da Espanha,
e a razão escrita para o criar foi que «sem ficha não havia contrato de campos, registo de
versão nem `ACCESS_METHOD` auditável». O recorte italiano alimentava `ITALY-HERO-CASES-V1`
sem nenhuma das três. Uma régua que decide de um jeito na Espanha e de outro na Itália não é
uma régua.

**`IT-T3-006` desceu para YELLOW a meio deste passo, e voltou a GREEN — e é o erro mais
instrutivo do dia, porque foi meu.** Ao aplicar à Itália o mesmo critério que negava ficha a
`IT-T3-003`, escrevi na ficha `RAW_EVIDENCE_PRESERVED: NÃO — nenhum byte dela está
versionado`. O repositório tinha, e tem, `data/samples/IT-T5-SENSORES/ersa-fvg-boll-07-frumento-orzo-2026-04-20.txt`:
o boletim **n.º 07 da mesma série**, texto integral, 9.381 bytes, com sha256 registado em
dois artefactos que declaram `EVIDENCE_STATE: PRESERVED`. A série de *colture erbacee* do
FVG é **uma numeração só, alternando culturas** — o `Boll_15_MAIS` do exemplo e este n.º 07
são números do mesmo boletim, da mesma página.

**O critério estava certo; a medição que o alimentava não existia.** Eu afirmei uma
ausência sem a medir, que é precisamente o que a lei zero da casa proíbe, e fi-lo dentro do
passo que passou o dia a corrigir esse defeito noutros ficheiros. Quem apanhou foi uma
revisão adversarial, com um `sha256sum`.

    AUSÊNCIA DE EVIDÊNCIA ≠ EVIDÊNCIA DE AUSÊNCIA
    RÉGUA APLICADA COM MEDIÇÃO INVENTADA = PREFERÊNCIA, NÃO RÉGUA

Ficou registado na própria ficha, e o atlas ganhou a lista nomeada das **13 fichas sem linha
`EVIDENCE`** — as outras 23 declaram-na, e os 23 caminhos existem. `tests/test_canonico.py`
passou a exigir que todo caminho declarado exista e que a lista das treze seja exacta.

**`LEDGER_ID_MISMATCH` são cinco entradas, não duas.** Além de `IT-T4-001-ETICHETTA` e
`IT-T3-LOTTA-OBBLIGATORIA`, também `IT-T3-LAMMA` e `IT-T3-OP` — e sobretudo
**`ES-T7-001..027`**, a rede técnica espanhola: **27 fontes numa ficha só, que valem 0 na
contagem** porque um intervalo não casa com a régua. É o maior `LEDGER_ID_MISMATCH` da casa,
é anterior a `bdb57cf`, e nunca tinha sido declarado — sem essa linha a varredura mecânica
devolve 52 tokens fora das fichas em vez de 33 e o portão fica irreprodutível.
`FICHA_DOCUMENTADA != SOURCE_ID_CONTADO` · `INTERVALO != ID`.

**O placar deixou de ser digitado.** As linhas por país e a tabela de cobertura por
território passaram a ser **derivadas das linhas `VERDICT:` das próprias fichas**, e
`tests/test_canonico.py` reprova quando discordam. Antes, mover um GREEN da Espanha para a
Itália, trocar o veredito de uma ficha sem tocar no placar, destruir a linha da Itália na
tabela de cobertura ou apagar a secção de reconciliação inteira **não reprovava nada** — o
`SOURCE_GREEN_COUNT` saía da própria linha de Total, isto é, certificava-se a si mesmo. A
tabela por território ganhou a coluna **T13**, que faltava inteira, e três células da linha
EUROPE não correspondiam a ficha nenhuma.

### 3.2 · Os 34 IDs que aparecem no repositório sem ficha

Varredura mecânica e reprodutível sobre `data/`, `scripts/`, `docs/`, `research/` e o portal.
Nenhum fica em silêncio — o quadro completo está em
`docs/fontes/ATLAS-DE-FONTES-EAME.md`, secção *RECONCILIAÇÃO DE SOURCE_IDs USADOS FORA DO ATLAS*:

```
varredura                       = 91 tokens · 58 dentro das fichas · 33 fora
SOURCE_IDS_WITHOUT_ATLAS_ENTRY  = 0 não classificados · 33 classificados
  A · reconciliados (mesmo objecto, outro nome)          IT-T3-004, IT-T3-ER-MODENA,
                                                         IT-T3-LOTTA-B, IT-T5-001-B, IT-SRC-*
  B · PROBED_CANDIDATE / NOT_PROMOTED                    16 IDs, só no probe e no script que o gera
  C · documentados só no mapa nacional                   4 IDs
  D · anteriores a bdb57cf                               13 IDs
NOVOS DESTE PASSO SEM FICHA     = 20
DADO PUBLICADO ÓRFÃO DE FONTE   = 0
```

`tests/test_canonico.py` **refaz esta varredura** e reprova se aparecer um token no
namespace canónico que nenhum grupo nomeie. Antes, apagar a secção inteira passava.

A identidade `IT-T3-004 ≡ IT-T3-006` está declarada como **INFERIDA**, não comprovada:
nenhuma das duas medições preservou URL, e por isso a identidade não é verificável no
repositório. Numa tabela cujas colunas se chamam «É, comprovadamente» e «Prova», uma
inferência tinha de dizer o seu nome.

**`IT-T3-004` e `IT-T3-006` eram a mesma fonte com dois IDs** — o Friuli-Venezia Giulia,
medido duas vezes. Na primeira rodada leu-se a página-mãe das *colture erbacee* e concluiu-se
«nenhum bollettino de milho»; na segunda, pela subpágina `bollettini-2026`, apareceram **10
boletins de milho em 2026**. O ID canónico é `IT-T3-006`. A manchete negativa do mapa
nacional — *«o sistema italiano de boletins não é feito para o milho»* — continua verdadeira
para Veneto, Lombardia e Piemonte, **e é falsa para o Friuli**. O corpo do mapa não foi
reescrito: a medição de 30/08 é registo, e apagá-la faria a régua parecer sempre certa.

---

## 4. A ferramenta que existe para o número não envelhecer estava parada

`scripts/metricas_canonicas.py --sync` abortava com
`ValueError: Cannot specify ',' with 's'` num marcador de **exemplo** (`<!--M:NOME-->`) escrito
dentro do handoff. Como os `.md` da raiz são os últimos do walk, o handoff publicava
**649** e **329** testes e **37** SOURCE_IDs sem nada reprovar — e o `--sync` que deveria
consertar isso nunca chegava lá.

Duas correcções: um `METRIC_ID` sem dono no ledger passa a ser **deixado intacto** em vez de
derrubar o comando; e o exemplo no handoff deixa de ser uma marcação viva que engolia a
seguinte. **Defeito pré-existente a `bdb57cf`** — reproduzido na base antes de se lhe tocar.

Dois testes que reprovavam um documento **certo** também foram corrigidos: exigiam `1309`
cru onde o dono do número escreve `1.309`. `FORMATO != VALOR`.

---

## 5. Portões

```
CAMINHOS PERDIDOS (dos dois pais)      = 0
SÍMBOLOS E MÉTODOS PERDIDOS            = 2, ambos DELIBERADOS e nomeados abaixo
CANONICAL_VALID_CONTENT_LOST           = 0
SOURCE_VALID_CONTENT_LOST              = 0
FACT_FALSE_POSITIVE_REGRESSIONS        = 0
CONFIRMED_FOCUS_SILENT_LOSS            = 0
CANONICAL_LABEL_READER                 = IT-ROTULOS-PARES-V3
CANONICAL_LABEL_PAIRS                  = 2928 pares · 128 rótulos com par
OLDER_LABEL_READER_CANONICAL_AUTHORITY = NO
SOURCE_IDS_WITHOUT_ATLAS_ENTRY         = 0 não classificados (33 classificados, razão medida)
```

**`CANONICAL_VALID_CONTENT_LOST = 0` medido por CAMINHO é fraco, e foi assim que eu o
publiquei da primeira vez.** A revisão adversarial mostrou perda de conteúdo dentro de
caminhos presentes dos dois lados. A medição passou a ser por **símbolo de topo e método de
teste**, contra os dois pais, e devolve duas diferenças — as duas deliberadas, as duas
nomeadas:

| o que | face a | por quê |
|---|---|---|
| 12 símbolos de `scripts/linkedin_sensores.py` (`coletar`, `ler_post`, `relevancia`, `ACTOR_PERFIL`…) | `bdb57cf` | é o colector pago que pedia `searchQuery` a um ator que não lê esse campo: devolveu `SUCCEEDED` oito vezes, com o mesmo consultor de cibersegurança, e cobrou as oito. A ref removeu-o **de propósito** e escreveu porquê; o merge tinha-o reinstalado, com o workflow a corrê-lo com `APIFY_TOKEN_POOL`. `WRONG_INPUT_CONTRACT != WRONG_PLATFORM`. Os oito nomes, os tectos e a janela — o que continua verdadeiro — ficam |
| `test_as_vinte_e_uma_estao_presentes` | `b929879` | renomeado para `..._vinte_e_duas_...`: entrou a regressão `PARSER_SILENCE != NO_PRODUCT`. O método não desapareceu, mudou de nome com o número que o nome afirma |

Nenhuma das duas é perda silenciosa, que é a única espécie que conta.

### 5.1 · Os dois harnesses

Medidos contra `bdb57cf` restaurado, com o mesmo comando, e comparados **por identificador
de teste** — não por contagem de módulo.

| | por módulo | processo único |
|---|---|---|
| base `bdb57cf` | 18 falhas | 24 falhas/erros |
| depois de tudo | 10 falhas | 16 falhas/erros |
| **`NEW_TEST_REGRESSIONS`** | **0** | **0** |
| vermelhos pré-existentes consertados | 8 | 8 |

```
tests: 846 -> 1380
```

**Os dois harnesses passaram a correr o mesmo conjunto.** `tests/test_comunicacao.py`
levantava `SystemExit(1)` na importação e matava a recolha inteira do pytest, o que obrigava
o harness de processo único a correr sempre com `--ignore` — e escondia por trás disso um
vermelho real. Fechado (ver §5.3), o pytest corre agora sem exclusão nenhuma:
`10 failed, 1391 passed, 19 skipped, 6 errors`. A comparação com a base acima é feita com o
MESMO comando dos dois lados, senão não seria comparação. **`no tests ran` nunca é suíte
limpa.**

### 5.3 · Os dez vermelhos que ficam, nomeados

`NEW_TEST_REGRESSIONS = 0` **não quer dizer suíte limpa.** O handoff dizia
`0 falhas, 0 erros, 0 pulados` na mesma linha que manda a próxima conta correr
`python3 -m unittest discover -s tests` — e esse comando imprime dez falhas. A contagem de
testes era o único campo daquela linha que algum teste guardava; o resto podia dizer
qualquer coisa. Agora diz o que é, e ficam nomeados:

| módulo | falhas | o que reclamam |
|---|---|---|
| `tests/test_evidence.py` | 5 | amostras sem `CAPTURED_AT`/origem declarados e três com `SOURCE_LOCATION`/`FACT_LOCATION` incoerentes |
| `tests/test_proveniencia.py` | 3 | o inventário do bruto pago não bate com o diretório real (tamanho, órfãos, lista) |
| `tests/test_adama_es_gate.py` | 1 | a migração nova não tem incompatibilidade provada |
| `tests/test_migrations.py` | 1 | `.gz` novo entrou no git |

**Os dez são anteriores a `bdb57cf`** e estão medidos como tal nos dois harnesses. Nenhum
é desta integração, e nenhum é desculpa: são dívida nomeada, que é o oposto de dívida
escondida.

**O que mudou para melhor, e é medível:** `tests/test_comunicacao.py` deixou de morrer na
importação. Ele levantava `SystemExit(1)` e matava a recolha inteira do `pytest`, o que
obrigava o harness de processo único a correr sempre com `--ignore` — e por trás disso
escondia um vermelho real, «nenhuma casa nasce autorizada», que comparava `set()` com
`{'NO'}` porque o crosswalk que alimenta o universo não é versionado. `EMPTY_SET !=
PROVEN_NO`: a prova agora distingue *nenhuma casa nasce autorizada* de *não há casa
nenhuma*, e volta a reprovar se o crosswalk aparecer e as casas continuarem zero. **Os dois
harnesses passaram a correr o mesmo conjunto.**

### 5.2 · A matriz de mutação — a prova de que os testes mordem

| mutação | testes que reprovam |
|---|---|
| repor `LABEL_COVERAGE.PCT = 100.0` | 2 |
| `LABEL_READ_COVERAGE = 163` | 3 |
| tirar um mudo da lista da dívida | 4 |
| gerador: `READ` passa a medir `DOWNLOAD` | 1 |
| `CANONICAL_AUTHORITY = YES` | 1 |
| leitor canónico com data anterior ao legado | 1 |
| campo "exclusivo" que não é exclusivo | 1 |
| tirar a correcção do documento do piloto | 1 |
| reverter C1 / C2 / C3 / C4 de `fato_local.py` | 2 / 2 / 2 / 3 |
| `CABECALHOS_DE_COLUNA = set()` | **0 → 2** |
| `PALAVRAS_ADMINISTRATIVAS = ()` | **0 → 1** |
| repor a divisão da dívida perguntando só ao leitor canónico | **0 → 3** |
| repor `IT-T3-006` a GREEN sem a linha `EVIDENCE` | **0 → 1** |
| CHECK do banco reescrito como `= any (array[…])` com `MODELLED_RISK` | 2 |
| CHECK do banco numa forma que o parser não reconhece | 3 |
| repor a tradução do manifesto em `sensor_coleta.py` | 1 |
| **controlo, tudo restaurado** | **0** |

**As quatro linhas a negrito são a segunda ronda, e as quatro davam ZERO antes dela.** A
quinta correcção de `fato_local.py` — `CAPTURA != NOME DE LUGAR`, a que trouxe
`_limpa_nome` — nem sequer tinha linha nesta matriz, e era precisamente aquela cuja
reversão parcial não reprovava nada: esvaziar `CABECALHOS_DE_COLUNA` devolvia o cabeçalho
de coluna `Maturazione` como lugar do facto com as 1.386 provas verdes, porque o teste
olhava só para a FORMA do nome — quebra de linha, dígito, espaço duplo, comprimento — e
para a quinta forma lia a lista da própria implementação. **Um teste que percorre a
constante que devia testar fica vácuo no instante em que alguém a esvazia.** Agora a lista
está escrita no teste, `_limpa_nome` tem provas directas com literais, e o conjunto dos 24
lugares que o corpus produz está pregado — mudar uma regra passa a exigir declarar o que
ela mudou.

**A primeira matriz media as mutações que eu tinha pensado.** A revisão adversarial mediu as
que eu não tinha: sete mutações ao bloco do leitor canónico e três à cobertura **não
reprovavam nada** — trocar as doze linhas não cobertas por lixo mantendo o comprimento,
esvaziar a lista de campos exclusivos, falsificar o método, pôr o portão em `FAIL`, apagar o
ficheiro do portão do repositório, substituir os 2.928 pares por 2.927 cópias de uma linha,
truncar os 40 textos de rótulo a zero bytes. Todas reprovam agora, e é por isso que os dois
ficheiros de teste cresceram de 10 e 15 provas para 22 e 21.

---

## 6 · AS DUAS REVISÕES ADVERSARIAIS, E O QUE ELAS MUDARAM

O passo foi revisto **duas vezes**, e a segunda vez foi sobre as correcções da primeira —
porque uma correcção não revista é só uma mudança.

**Primeira ronda, seis revisores, antes de qualquer publicação.** Trouxe 46 achados, e os
que sobreviveram à reprodução mudaram o resultado em toda a parte:

| onde | o que estava errado |
|---|---|
| `fato_local.py` | seis famílias de falso positivo **vivas no corpus real**: o endereço do titular num rótulo virava lugar do facto em cinco ficheiros; a chuva virava ocorrência fitossanitária nos dois boletins mais ricos da Itália; um timbre de cinco linhas virava `FACT_LOCATION`; `rischio non è elevato` afirmava o oposto do texto |
| cobertura | três nomes de estágio mentiam, dois estágios não podiam falhar, e a prova da dívida era `len(ids)` — igual a si mesma por construção |
| leitor canónico | `37 de 49` era 39, lia-se como usos quando é cultura, e sete mutações ao bloco não reprovavam nada |
| atlas | o placar certificava-se a si mesmo; a tabela por território não somava e faltava-lhe a coluna T13; `ES-T7-001..027` era o maior `LEDGER_ID_MISMATCH` da casa e nunca fora declarado |
| merge | **uma classe de teste da ref tinha sido deixada cair, e uma das suas provas reprova contra o resultado do merge**; o colector pago de LinkedIn tinha voltado ao lado defeituoso, com o workflow a corrê-lo com a chave |
| suíte | o handoff prometia `0 falhas` ao lado do comando que imprime dez |

**O achado mais caro foi o do merge**, e é o que corrige a minha própria declaração: eu tinha
publicado `SOURCE_VALID_CONTENT_LOST = 0` medindo **caminhos**, e havia perda de **conteúdo**
dentro de caminhos que existiam dos dois lados. Uma classe de seis provas que só a ref tinha
desapareceu na resolução, e a suíte ficava verde **em parte por causa disso**: uma das seis
reprova contra o código que o outro lado trouxe. `PATH_PRESENT != CONTENT_PRESERVED`.

**Segunda ronda, três workflows, sobre as correcções.** Nada foi publicado enquanto qualquer
revisor estava a correr — a regra que na integração anterior eu quebrei, e que custou dois
buracos reais descobertos depois do push.

## 7. Próximo passo

`NEXT_SINGLE_STEP` = **P0.2 · PASSO 04 — medir o próximo enxerto contra o novo HEAD**

**NÃO EXECUTADO.** Parado aqui, como mandado.
