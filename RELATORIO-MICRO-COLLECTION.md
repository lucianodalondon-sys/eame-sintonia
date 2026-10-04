# RELATÓRIO — MICRO-COLLECTION V1

A primeira missão desta casa que saiu à rede a sério.

```
INITIAL_HEAD   = b4c425fb2588116a480dcaa57b11fd04b63ab1b8
FINAL_HEAD     = 35b8911ed27366b672d78f2c7af075757b0aa812
                 — a árvore sobre a qual TUDO neste relatório foi medido.
                 Este ficheiro e a regeração de mapa que ele arrasta vêm no
                 commit seguinte: um relatório não pode nomear o próprio HEAD
                 sem mentir sobre o que mediu.
REMOTE_HEAD    = NÃO SEI — a branch `micro-collection-v1` ainda não existia no remoto
                 no arranque (`git rev-parse origin/micro-collection-v1` = unknown revision)
WORKTREE_CLEAN = SIM (antes e depois; medido por md5, não só por `git status`)
ACTUAL_LLM_MODEL = claude-opus-5
REQUESTED_LLM_MODEL = claude-opus-5   ·   coincidem
```

---

## ⚠️ O ACHADO QUE MANDA NO RESTO DO RELATÓRIO

O portão aprova oito fontes. O coletor desta árvore não sabe abrir nenhuma
delas.

```
portão   curadoria/collection_gate.py        COLLECTION_ELIGIBLE = 8
coletor  coleta/italy_pilot_collect.mjs      CONTRACT_IDS = 14 · PILOT_SOURCES = 7
         das 8 elegíveis, com contrato executável:  0
         interseção entre «o que o portão aprova» e «o que o coletor conhece»:  0
```

Medido em runtime, sem rede, pela própria porta da Collection:

```
IT-T7-043   portão: ADMITIDA=True  ELIGIBLE
            coletor: CODIGO=2  FONTE_DESCONHECIDA — «este coletor percorre
            IT-T3-005, IT-T2-002, IT-T2-004, IT-T3-002, IT-T3-010, IT-T3-008,
            IT-T4-001. Nao se finge que correu.»

IT-T3-010   portão: ADMITIDA=False  READY_LEGACY  → BLOQUEADA_PELO_CURATOR
            coletor: conhece-a — mas o portão não a deixa passar
```

Os dois conjuntos são **disjuntos**. Quem o portão aprova, o coletor não abre;
quem o coletor abre, o portão recusa.

A tradução que falta — os contratos do curador
(`curadoria/italy_contracts_curator.json`, 81 fontes, vocabulário
`MATCH`/`INDEX_URL`/`LINK_PATTERN`) para a tabela do motor de rota — existe,
mas **noutra branch**: `aquisicao-detalhe-v1`, em
`regras/italy_contracts_onboarded.json` (173 fontes, cobre 7 das 8). São 16
commits de distância, sobre uma divergência de ~53 mil linhas.

Trazer essa tradução é uma missão de *cutover*, não de micro-recolha. Foi
decisão do dono não a fazer aqui.

**Consequência honesta:** a cadeia `COLLECTION_ELIGIBLE → RUN → OBSERVATION →
RAW → DERIVED → ADMISSION → SALA` **parte no primeiro elo** para estas oito
fontes. Tudo o que se segue mede a ida à fonte por um caminho que já existe
nesta árvore e já fala a língua destes contratos — e **não** chega ao acervo.

---

## FASE 0 — PRÉ-VOO

| o que se mediu | valor |
|---|---|
| `COLLECTION_ELIGIBLE` (runtime, não JSON velho) | **8** |
| painel do portão | READY_TOTAL 87 · READY_CURRENT 10 · READY_LEGACY 77 · HUMAN_REVIEW 3 |
| suíte de base | **279 testes OK**, 16,6 s |
| observações no livro italiano, antes | 184 (34 corridas) — nenhuma das 8 fontes |
| Sala canónica | **VIVA** — `127.0.0.1:54330/sala_italia` |
| supervisor a correr noutra worktree | `source-curator-supervisor-v1`, PID 88644 — não toca nos nossos ficheiros |

Acervo antes (Sala canónica):

```
raw_asset 1072 · collection_run 369 · storage_object 938
derived_artifact 758 · sala_de_espera 46
```

### O egresso mudou a meio da missão

```
pré-voo   (17:25Z)  EGRESSO = BR   177.95.91.48   São Paulo    AS27699 TELEFÔNICA BRASIL S.A
depois    (17:36Z)  EGRESSO = IT   146.70.182.38  Milan, Lombardy  AS9009 M247 Europe SRL
```

O dono autorizou colher com egresso BR. **Duas corridas correram nessa
autorização.** Depois ligou a VPN italiana e revogou a decisão anterior. Eu
medi o egresso italiano por dois medidores independentes (`ipinfo.io` e
`api.ipify.org`, mesmo IP) e o dono autorizou **uma visita extra** a partir de
Itália — o que leva o tecto declarado de 2 corridas para 3.

**Cada número deste relatório traz o egresso que ele realmente teve.** Não é
verdade que «a colheita real correu com IT»: duas terças partes dela correu do
Brasil, e está dito onde.

Nenhuma das 8 fontes está registada como exigindo rota italiana — a vista
`v_fonte_exige_rota_italiana` da Sala está **vazia**.

---

## FASE 1 · 3 — AS CORRIDAS

```
RUN1  2026-09-21T17:31Z   EGRESSO=BR  177.95.91.48  São Paulo   AS27699 Telefônica
RUN2  2026-09-21T17:34Z   EGRESSO=BR  177.95.91.48  São Paulo   AS27699 Telefônica
RUN3  2026-09-21T17:38Z   EGRESSO=IT  146.70.182.38 Milan       AS9009 M247 Europe SRL
      (egresso reconfirmado no fim da RUN3: continuava 146.70.182.38 / Milan / IT)
```

| | RUN1 (BR) | RUN2 (BR) | RUN3 (IT) |
|---|---|---|---|
| fontes tentadas | 8 | 8 | 8 |
| itens enumerados | 125 | 125 | 116 |
| itens colhidos | 20 | 20 | 20 |
| **matéria real** | **19** | **19** | **20** |
| capas colhidas | 1 | 1 | 0 |
| pedidos | 35 | 35 | 35 |
| robots bloqueou | 1 | 1 | 1 |
| HTTP 403 · 429 | 0 · 0 | 0 · 0 | 0 · 0 |

Por fonte — enumerados → colhidos → matéria (RUN3, egresso IT):

```
IT-T10-018  myfruit.it                  HTTP 200   30 →  3 →  3
IT-T10-022  zootecnicainternational.com HTTP 200    9 →  3 →  3
IT-T5-041   crpv.it                     HTTP 200    6 →  3 →  3   (BR: robots não lido)
IT-T5-049   di3a.unict.it               HTTP 200    5 →  3 →  3
IT-T7-017   riuniteciv.com              HTTP 200   54 →  3 →  3
IT-T7-033   chianticlassico.com         —           0 →  0 →  0   (IT: robots não lido)
IT-T7-042   consorziobalsamico.it       HTTP 200   10 →  3 →  3
IT-T7-043   agrofarma.federchimica.it   HTTP 200    2 →  2 →  2
```

O tecto de 3 itens por fonte é meu, não da fonte: `riuniteciv.com` anunciou 54
itens e eu abri 3.

---

## FASE 2 — PROVA DE MATÉRIA REAL

Cada item aberto passou pelas três provas que a missão pediu, com os números
ao lado, pelo gate `CAPA_NAO_E_MATERIA/v1` (dono único:
`curadoria/retrato_html.py`).

```
MATERIA_REAL_PROVADA (RUN3, IT)  =  20/20
MATERIA_REAL_PROVADA (RUN1, BR)  =  19/20
CAPAS_COLHIDAS                   =  1   (RUN1 e RUN2, egresso BR)
```

A capa, nomeada:

```
IT-T7-033  chianticlassico.com
  https://www.chianticlassico.com/news/e-learning-vuoi-diventare-un-esperto-di-chianti-classico/
  CAPA_NAO_E_MATERIA: 88 ligações para 1.920 caracteres, 646 em parágrafos
```

Não foi maquilhada: conta como falha, e a fonte está nomeada.

Amostra do que é matéria de verdade (RUN1, BR):

```
myfruit.it/news/despar-nord-wecity-riparte-il-progetto-mobilita-sostenibile
  98.379 bytes · 9.184 caracteres · 4.614 em parágrafos · 145 ligações · CONTENT
zootecnicainternational.com/news/dr-james-jim-mckay-obituary-2026/
  174.612 bytes · 3.264 em parágrafos · CONTENT
```

Todos os 20 itens têm URL **diferente** do índice (`URL_DIFERE_DO_INDICE =
true` em todos).

---

## FASE 3 — INCREMENTALIDADE

RUN1 → RUN2, mesmas 8 fontes, 2 minutos e 25 segundos depois, mesmo egresso:

```
ITENS_NOVOS_RUN2        = 0
ITENS_REPETIDOS_RUN2    = 20
TEXTO IDÊNTICO          = 20/20   (mesmo TEXT_SHA256)
DUPLICADOS_REJEITADOS   = 0 — este instrumento não guarda, logo não deduplica
```

**Isto está certo, e não é nem sucesso nem falha.** Nenhum destes oito sítios
publicou nada em 2 minutos e meio. O que a segunda visita prova é outra coisa,
e é útil: o leitor é **determinístico** — leu duas vezes e contou a mesma
coisa, ao carácter.

### E o que a visita de Itália mostrou que a do Brasil não mostrava

17 dos 20 itens são o mesmo endereço nas duas. Desses 17:

```
14/17   texto idêntico entre BR e IT
 3/17   TEXT_SHA256 DIFERENTE — e tudo o resto igual
```

Os três são de `myfruit.it`, e a comparação é desconfortavelmente exacta:

```
                        bytes    caracteres   parágrafos   ligações   TEXT_SHA256
pam-panorama…  BR/RUN1  93.788     6.139        1.657        144      1a75830f13
pam-panorama…  BR/RUN2  93.788     6.139        1.657        144      1a75830f13
pam-panorama…  IT/RUN3  93.788     6.139        1.657        144      19b1bf2f31   ← mudou
```

Medi mais: duas leituras seguidas do mesmo endereço, do mesmo egresso IT, dão
**exactamente o mesmo** `TEXT_SHA256`. Logo não é ruído de leitura nem o token
`_token` escondido no HTML (esse muda a cada leitura e o retrato não o vê).

**Porque é que o texto muda entre países sem mudar de tamanho: `NÃO SEI`.**
O que fica provado e importa:

> Um controlo de novidade feito **só por hash** contaria estes 3 itens como
> «documento novo» a cada mudança de saída de rede, sem que uma única coisa
> mensurável tenha mudado. É a lei `NEW_HASH != NEW_SEMANTIC_FACT` desta casa,
> apanhada em campo.

---

## FASE 4 — SALA

```
SALA_ANTES              = 46 linhas   ·   SALA_DEPOIS = 46 linhas
RAW_ANTES               = 1072        ·   RAW_DEPOIS = 1072
DERIVED_ANTES           = 758         ·   DERIVED_DEPOIS = 758
COLLECTION_RUN antes    = 369         ·   depois = 369
STORAGE_OBJECT antes    = 938         ·   depois = 938

ADMITIDAS_PELA_PORTA    = 0
BYPASS_DA_ADMISSAO      = 0
```

Nada chegou à Sala, e **isso não é uma falha silenciosa: é o achado do topo
deste relatório.** A cadeia para antes do primeiro elo, porque o coletor não
conhece estas fontes. Não inventei porta lateral e não escrevi na Sala à mão.

```
CAMPOS_VAZIOS_NA_SALA (do que chegou nesta missão) = não se aplica: nada chegou.
```

Para referência — e **não é desta missão** — as 46 linhas que já lá estavam
têm todos os campos canónicos preenchidos (46/46 em `fact_time`,
`published_at`, `observed_at`, `captured_at`, `source_location`,
`fact_location`, `run_id`, `raw_observation_id`, `item_id`, `corrida_sha256`)
e foram admitidas por `pertence ao universo v5`.

⚠️ A Sala canónica é partilhada com outras sessões (há agente vivo em
`cutover-v2`). As contagens são do instante em que as li.

---

## FASE 5 — CUSTO E POLÍTICA

```
PEDIDOS_TOTAL          = 105   (3 corridas × 35)
PAID_USD               = 0.00  — nenhuma rota paga foi tocada; tudo HTTP público
EGRESSO                = BR nas RUN1/RUN2 · IT na RUN3 (detalhe acima)
HTTP_429               = 0
HTTP_403               = 0
ROBOTS_RESPEITADOS     = SIM — nenhum bloqueio foi contornado
```

Pedidos por domínio (RUN1+RUN2, egresso BR):

```
myfruit.it 10 · zootecnicainternational.com 10 · di3a.unict.it 10
riuniteciv.com 10 · chianticlassico.com 10 · consorziobalsamico.it 10
agrofarma.federchimica.it 8 · crpv.it 2
```

### ⚠️ ROBOTS_BLOCKS = 3, e nenhum deles é uma proibição

Este é o segundo defeito que a missão apanhou, e apanhou-o **no meu próprio
instrumento**.

`curadoria/gate_de_rota.py` devolve, de propósito, um `Disallow: /` quando
**não consegue ler** o `robots.txt` — «UNKNOWN, tratado como barrado por
prudência». Fechar assim está certo. O que estava errado era o meu registo
guardar só o `False`, e a corrida sair a dizer *«o robots.txt vivo não permite
a entrada»* — uma proibição afirmada que ninguém leu.

> **NÃO LI O ROBOTS ≠ O ROBOTS PROIBIU.**

Fui medir os três bloqueios um a um:

```
www.chianticlassico.com   robots.txt NÃO RESPONDE
                          urllib: URLError após 2 tentativas
                          curl:   http=000, 20,1 s, 0 bytes
                          → ROBOTS_NAO_LIDO, não Disallow

www.crpv.it               NÃO PUBLICA robots.txt — faz HTTP 301 para o site,
                          e o que chega é HTML
                          → sem regra publicada = sem proibição (a norma)
                          → o bloqueio no RUN1/RUN2 (BR) foi o mesmo «não li»
```

```
ROBOTS_DISALLOW publicado, em 8 fontes  =  0
ROBOTS_NAO_LIDO                          =  3
```

O instrumento foi corrigido: a razão viaja agora a par do veredito e
`ROBOTS_DISALLOW` conta-se separado de `ROBOTS_NAO_LIDO`. Correcção validada
ao vivo. **As três corridas guardadas não trazem essa separação** — ela foi
recuperada por medição directa, e está aqui.

Um efeito secundário que vale registar: `crpv.it` devolve **HTML** em
`/robots.txt`. O parser lê HTML sem encontrar regras e liberta tudo. Deu certo
por sorte; se aquele HTML contivesse por acaso uma linha `Disallow: /`, seria
lida como regra. Fica como dívida nomeada, não como conserto apressado.

---

## GATES

```
G-ELIG   PASS   105 pedidos, 8 domínios, 0 fora do perímetro.
                LEGACY_TOUCHED = 0. Provado pelo log de pedidos, não pela intenção.

G-ISO    PASS   md5 idêntico antes e depois, em todos os livros:
                LIFECYCLE-LEDGER-V1.json   1e04c39eb66c566146ea89b4195f7b3a
                LIFECYCLE-QUEUE-V1.json    87be1ef3daf531f992b02c6a40963409
                LIFECYCLE-EVIDENCE-V1.json 8ed1d9e108a4e0fce1dba4cff8e1acf1
                italy_contracts_curator    1f26d9a8931ffdc486dc4f466c7d8499
                observations.ndjson        690ca8362aa82fad0cd6b9495709a7c9
                runs.ndjson                593b55e469cc34bfd2e6e25967cd1442

G-SAFE   PASS   nenhum teste saiu à rede. A sonda da cadeia usou a porta real e
                parou no portão/CLI, sem pedido nenhum. Tudo o que saiu à rede
                saiu por `medidas/micro_colheita.py`, chamado à mão, e está no
                log dos três recibos. Escrita no acervo: ZERO — nem da colheita
                nem dos testes.

G-REG    PASS   TESTS_BEFORE 279 / AFTER 279 / NEW_FAILURES = 0

G-MAP    PASS   SYSTEM_MAP_CHECK = PASS
                O validador reprovou primeiro, e com razão: `micro_colheita.py`
                era código novo sem peça no mapa. Declarado como
                C-MICRO-COLHEITA em Z-MEDIDAS; cadeia REGERAR + VALIDAR = OK.
```

---

## VEREDITO

```
COLLECTION_ELIGIBLE_MEDIDO = 8
FONTES_TENTADAS            = 8        LEGACY_TOUCHED = 0
RUN1_ITENS = 20 (BR) · RUN2_ITENS = 20 (BR) · RUN3_ITENS = 20 (IT)
ITENS_NOVOS_RUN2 = 0                  DUPLICADOS_REJEITADOS = 0
MATERIA_REAL_PROVADA = 20/20 (IT) · 19/20 (BR)
CAPAS_COLHIDAS = 1                    → IT-T7-033 chianticlassico.com

RAW_ANTES/DEPOIS = 1072/1072          DERIVED_ANTES/DEPOIS = 758/758
SALA_ANTES/DEPOIS = 46/46
ADMITIDAS_PELA_PORTA = 0              BYPASS_DA_ADMISSAO = 0
CAMPOS_VAZIOS_NA_SALA = não se aplica — nada chegou

PEDIDOS_TOTAL = 105 · PAID_USD = 0.00
EGRESSO = BR (RUN1, RUN2) · IT (RUN3)
ROBOTS_BLOCKS = 3, dos quais ROBOTS_DISALLOW = 0 e ROBOTS_NAO_LIDO = 3
HTTP_429 = 0 · HTTP_403 = 0
TESTS_BEFORE 279 / AFTER 279 / NEW_FAILURES = 0
SYSTEM_MAP_CHECK = PASS

MICRO_COLLECTION_RESULT = PARTIAL
BIG_COLLECTION_ALLOWED  = NO
```

**PARTIAL, e o porquê em duas linhas.** A metade que dependia das fontes
passou inteira: 8 de 8 visitadas, 105 pedidos, zero fora do perímetro, zero
403, zero 429, custo zero, 20 de 20 itens provados como matéria real. A metade
que dependia da nossa própria casa não correu: **nada chegou ao RAW, ao
DERIVED ou à Sala**, porque o coletor desta árvore não conhece nenhuma das
oito fontes que o portão aprova.

### NÃO SEI — a lista honesta

1. **Porque é que 3 páginas de `myfruit.it` mudam de texto entre egresso BR e
   IT** mantendo bytes, caracteres, parágrafos e ligações exactamente iguais.
   Não é ruído de leitura — dentro do mesmo egresso o hash é estável.
2. **Se o bloqueio de `crpv.it` no RUN1/RUN2 (BR) foi mesmo um timeout.** Não
   pode ser remedido: a VPN está ligada e o estado BR já não existe. O que se
   sabe é que não foi um `Disallow` publicado — `crpv.it` não publica robots.
3. **Se `chianticlassico.com` está em baixo ou a barrar a nossa saída de rede.**
   O `/robots.txt` não responde a partir de IT; as páginas responderam a partir
   de BR. Uma leitura, um momento — não é um veredito sobre a fonte.
4. **`REMOTE_HEAD` no arranque.** A branch não existia no remoto.
5. **Quanto do acervo da Sala se moveu por outras sessões** durante a missão.
   Há agente vivo noutra worktree sobre o mesmo banco; li instantes, não uma
   fotografia estável.
6. **Se trazer a tradução de `aquisicao-detalhe-v1` fecharia a cadeia sem
   partir mais nada.** Não foi tentado — é decisão de *cutover*, e o dono
   decidiu não a fazer aqui.

---

## EM PALAVRAS SIMPLES

Imagina uma biblioteca que quer recortar notícias de oito jornais italianos.

**O primeiro problema é de dentro de casa.** O porteiro da biblioteca tem uma
lista de oito jornais autorizados. O empregado que vai à rua buscar jornais tem
outra lista, com sete nomes. **As duas listas não têm um único nome em comum.**
O porteiro deixa entrar quem o empregado não sabe ir buscar, e o empregado só
sabe ir buscar quem o porteiro manda voltar para trás. Não é que alguém se
enganou a escrever: a folha que traduz uma lista para a outra ficou noutra
gaveta da casa — noutro ramo do trabalho — e nunca chegou a esta.

**Mesmo assim fui à rua ver os oito jornais**, com um carrinho emprestado que
já sabia o caminho. Bati à porta de oito, sete abriram. Trouxe 20 recortes.

**Eram notícias mesmo, ou só a capa do jornal?** Havia essa dúvida, e há uma
régua para ela: uma notícia tem texto corrido; uma capa tem muitos títulos e
pouca letra. Passei os 20 pela régua. **Dezanove eram notícia.** Um era capa —
uma página de curso do Chianti Classico, com 88 ligações e três parágrafos de
texto. Está nomeada, não foi disfarçada de notícia.

**A segunda visita trouxe coisa nova?** Não: zero. Voltei dois minutos e meio
depois e estava tudo igual, à letra. **E isso está certo** — nenhum jornal
publica nada em dois minutos e meio. O que a segunda visita provou foi outra
coisa, e vale: o meu carrinho conta sempre a mesma coisa, não inventa
diferenças.

**A meio, tu ligaste a internet pela Itália.** As duas primeiras visitas já
tinham acontecido, e tinham saído pelo Brasil — isso está escrito ao lado de
cada número, porque trocar a etiqueta depois seria mentir. Fui uma terceira
vez, agora por Milão. E apareceu uma coisa curiosa: **três páginas do mesmo
jornal trazem texto diferente conforme o país de onde se chega**, com
exactamente o mesmo número de letras, de parágrafos e de ligações. Porquê, não
sei. Mas sei o que isso custa se ninguém olhar: quem decidir «é notícia nova»
só por o texto não ser igual ao de ontem, vai guardar essas três outra vez a
cada mudança de rota, achando que são novas.

**E aquele «o jornal proibiu-nos de entrar»?** Também tive de o desmentir — a
mim próprio. Dois jornais apareceram como «proibidos». Fui ver à mão: **nenhum
dos dois nos proibiu.** Um simplesmente não atende naquela porta, o outro nem
tem porta dessas. O meu carrinho é que, quando não consegue ler o aviso na
entrada, fica à porta por prudência — e faz bem — mas depois **escrevia no
relatório que tinha lido um aviso a proibir.** Não tinha lido nada. Corrigi o
carrinho: agora diz «não consegui ler» em vez de «proibiram-me». Das oito
fontes, **as que nos proibiram mesmo são zero.**

**Chegou alguma coisa ao arquivo da biblioteca?** Não. Nem uma folha. E isto é
o mais importante do relatório: **não chegou, e eu não fiz de conta que
chegou.** Não havia como entrar pela porta certa, e entrar por uma janela seria
pôr no arquivo papéis sem registo de entrada — exactamente o problema que esta
casa passou meses a limpar. As prateleiras estão com os mesmos números do
início: 1.072, 758, 46.

**Custou dinheiro?** Zero. Nenhum dos 105 pedidos passou por serviço pago.
Nenhum jornal nos mandou embora com um «páre» (zero 403, zero 429).

**O que falta para o material chegar ao arquivo:** escrever a tal folha de
tradução entre as duas listas. É trabalho declarado, não adivinhação — a folha
já existe noutro ramo e pode ser trazida. Mas é obra para outra missão, com
tempo para a fazer bem.

**A colheita grande continua barrada.** `BIG_COLLECTION_ALLOWED = NO`.

---

*Evidência completa, pedido a pedido, com o egresso de cada corrida:*
`medidas/MICRO-COLLECTION-RUN1-BR-V1.json` ·
`medidas/MICRO-COLLECTION-RUN2-BR-V1.json` ·
`medidas/MICRO-COLLECTION-RUN3-IT-V1.json`
*O instrumento:* `medidas/micro_colheita.py`
