# HANDOFF · ACERVO → PACOTE · V1

```
BRANCH        claude/acervo-to-package-intelligence-v1
BASE          5fac11f  (claude/opportunity-commercial-priority-v1, tip)
BUILD_ID      V21-4f4fac5a80d18df8
PORTAL        NÃO TOCADO — nenhum arquivo de italia-portale/ foi editado
DEMO          NÃO TOCADA · nenhum deploy · nenhum merge
CONSUMIDOR    claude/integration-acervo-portal-v1
```

Esta linhagem não entrega tela. Entrega um **pacote canônico melhor**, e a conta
de quanto ele melhorou.

---

## 1 · O QUE ATRAVESSOU

A outra linhagem provou que `PACOTE → PORTAL` não perde nada: 6.895 IDs entram,
6.895 saem. A perda estava antes, e não tinha medidor. Agora tem.

| FAMÍLIA | ACERVO | ANTES no pacote | AGORA | TEXTO QUE ATRAVESSA |
|---|---|---|---|---|
| TRANSCRIPTS | 184 objetos | **0** | 184 (160 com fala) | **5.167.243 ch** |
| SCIENCE (publicada) | — | 88 sem texto | 88 com abstract | **93.889 ch** em 81 |
| SCIENCE_CORPUS | 763 materiais | não existia | 763 com estado | **612.291 ch** em 618 |
| ADS · prova temporal | 1340 entidades | 27 ACTIVE sem data | 414 com data | 414/414 |

`ACERVO_PINNED` é agora uma camada de origem própria no registro central: **947
registros**, ao lado de `PREVIOUS_HANDOFF` (3.273) e `LAST_MILE` (3.463).
Mestre: **7.847 registros, 0 IDs duplicados**.

---

## 2 · COMO O ACERVO ENTRA — E POR QUE ISSO IMPORTA PARA VOCÊ

`competitor-activities.json` declarava, no cabeçalho, ter vindo de
`data/samples/META-EAME/META-ADS-ENTITIES-EAME-V1.json`. **Esse arquivo não
existe nesta linhagem.** Vive em `claude/eame-meta-competitor`, que não tem
merge-base com ela. Quem lesse a declaração e fosse procurar o insumo concluiria
que a proveniência mente — quando ela só estava noutra prateleira.

> **UM CAMINHO SEM REF NÃO É ENDEREÇO: É LEMBRANÇA DE ONDE O ARQUIVO ESTAVA.**

Agora todo insumo é endereçado por `(COMMIT, PATH, BLOB)` + `SHA256` do conteúdo,
em `data/acervo/ACERVO-SOURCES-V1.json` — **58 arquivos, 22.652.342 bytes**, de
dois refs:

```
sintonia/canonical          10af4a7accff88494eb097978c171601994a3422   56 arquivos
claude/eame-meta-competitor a2fad2d03e04ba071a7a66b0a502b5a515b5246b    2 arquivos
```

O byte continua vivendo na origem: **o manifesto tem 58 linhas, não 22 MB.** O
conteúdo entra no pacote, que é `.gitignore` e se reconstrói — custo zero no Git.

**Consequência para você:** `git fetch --all` antes de rodar a cadeia. Sem os
dois refs no object store, `scripts/acervo_fonte.py` **levanta** — de propósito.
Ele nunca devolve lista vazia.

---

## 3 · O QUE VOCÊ GANHA, POR FAMÍLIA

### A · TRANSCRIPTS.json — família nova

```
ACERVO_TOTAL      184 objetos de fala (o vídeo é o objeto)
PACKAGE_TOTAL     184   — os 24 sem texto entram com CLIENT_SAFE=false
ACERVO_CHARS      5.167.243
PACKAGE_CHARS     5.167.243
LOSS              0
```

Só fala, sem as 9 descrições de episódio do Spreaker: **151 objetos ·
5.036.308 ch**. Descrição de episódio não é fala transcrita, e sai do número de
fala sem sair do censo.

**A escada, e ela não sobe sozinha:**

```
VIDEO_EXISTS                    184
TRANSCRIPT_EXISTS               184
TRANSCRIPT_USABLE               160
TRANSCRIPT_INCLUDED_IN_PACKAGE  160
TRANSCRIPT_USED_AS_EVIDENCE       0   ← seu território
```

O último degrau é **seu**. O pacote leva os bytes e o `TEXT_SHA256`; quem faz um
cartão apoiar-se numa fala é o motor.

**Ponte já pronta:** dos vídeos que o pacote já citava, **5 têm fala — 117.304
caracteres**, e cada registro traz `SAME_VIDEO_AS_ACTIVITY_ID` apontando para o
`COMPETITOR_ACTIVITY` do mesmo vídeo. É a travessia mínima para provar utilidade
sem abrir frente nova.

**Antes de ligar isto a uma tela italiana, leia §5.**

### B · SCIENCE.json — mesma população, texto e prova novos

```
ACERVO_TOTAL       763
PACKAGE_TOTAL       88   (inalterado de propósito — ver abaixo)
ABSTRACTS_ACERVO   618 · 612.291 ch
ABSTRACTS_PACKAGE   81 ·  93.889 ch  (nos 88 publicados)
LOSS               675 registros, que agora vivem em SCIENCE-CORPUS.json
```

Os 88 **não mudaram de população**. Ganharam:

- `ABSTRACT_ORIGINAL` + `ABSTRACT_LANGUAGE` + `ABSTRACT_SHA256` + `ABSTRACT_SOURCE`
- `QUERY_CROP` / `QUERY_ISSUE` **vs** `PROVED_CROP` / `PROVED_ISSUE`, cada um com
  a **frase de evidência** que o sustenta (`o texto traz "grapevine"`)
- `CASE_ADHERENCE` · `CROP_IS_QUERY_TERM` · `ISSUE_IS_QUERY_TERM`

**Por que os 675 não entraram em `SCIENCE.json`:** não é filtro. **Nenhum passo
da cadeia lia o corpus de 763.** Os 88 são transporte 1:1 de um insumo antigo, e
os 86 com DOI são subconjunto estrito do corpus — 0 existem só do lado velho.
Despejar 675 registros na família que a tela já mostra mudaria a população de um
cartão publicado sem ninguém pedir. O corpus inteiro está em
`SCIENCE-CORPUS.json`, com `STATE` e razão por registro, e `SAME_ENTITY_AS`
ligando os 86 pares. **Adotá-lo é sua decisão, não efeito colateral desta cadeia.**

### C · COMPETITOR-ACTIVITIES.json — a prova temporal

```
ADS_WITH_TEMPORAL_PROOF_ACERVO    414 / 414
ADS_WITH_TEMPORAL_PROOF_PACKAGE   414 / 414   (era 0)
JUNÇÃO                            414 casaram · 0 falharam
ACTIVE_PROVED                      27   (era 0)
ACTIVE_UNKNOWN                      2
HISTORICAL                        385
```

`27 + 2 + 385 = 414`. **A regra de negócio não mudou para o número subir** — os
27 são exatamente os que já declaravam `ACTIVE`. O que mudou é que agora eles
carregam a data que os prova.

---

## 4 · O QUE VOCÊ **NÃO** PODE CONCLUIR

Três travas que o pacote agora carrega explicitamente. Ignorá-las transforma
transporte em mentira.

**1 · O termo de busca não é o conteúdo provado.**
`CROP` e `ISSUE` dos 88 são o termo que a busca usou. Medido: **39 de 88 são
`OFF_CASE`** — `IT-SCI-023` foi achado por «vite/flavescência» e o abstract fala
de *Drosophila suzukii* em **cereja**; `IT-SCI-024` fala de nematoides em prados
de feno na Lombardia. Se a tela imprimir «ciência sobre vite / flavescência»,
está imprimindo a **pergunta**, não a resposta.

`ISSUE_IDS` — que é **chave de junção**, lida por `v21_oportunidades.py`,
`v21_catraca.py` e `v21_necessidade.py` — passou a sair **só do provado**: 41 de
88, cada um com `PROVED_ISSUE_EVIDENCE` ao lado. Vazio ali significa «o texto não
prova alvo», não «a fonte não declarou».

> `CROP_IDS` **continua vindo do termo da busca** (87/88), como vinha antes desta
> missão. Não foi mexido: mudar a população de uma família publicada não é
> decisão desta linhagem. Está declarado em `CROP_IDS_ARE_QUERY_DERIVED`, com
> `PROVED_CROP_ID` (47/88) ao lado. **É dívida sua decidir.**

**2 · Uma leitura é um ponto, não uma linha.**
Profundidade de observação dos 414: **372 têm uma leitura, 20 têm duas, 22 têm
três**. Os 27 `ACTIVE_PROVED` têm, todos, **exatamente uma**. Isso prova o estado
em `2026-08-31T01:03:30+00:00` e mais nada — não prova hoje, não prova
continuidade. `FIRST_OBSERVED`/`LAST_OBSERVED` são **quando nós observamos**,
nunca quando o concorrente começou: `OBSERVATION_START != ACTIVITY_START`.

> **Quem imprimir o selo ATTIVO tem de imprimir a data ao lado.** O pacote leva
> a data; quantos dias ainda valem é decisão de quem mostra.

**3 · URL de vídeo não é transcrição.**
Cinco condições, e nenhuma implica a seguinte. O pacote citava 245 endereços de
vídeo e zero falas.

---

## 5 · LÍNGUA E PAÍS — LEIA ANTES DE LIGAR À TELA

A ingestão **não deduz país pela tela consumidora**. O que ela mede:

```
TRANSCRIÇÕES   país do fato   IT 126 · UNKNOWN 56 · FR 2
               língua         it 112 · UNKNOWN 72
               caso           IT 38 · FR 6 · ES 3 · UNKNOWN 137

ANÚNCIOS       36 dos 414 têm COUNTRY_REACHED=IT no pacote
               e country_reached=ES no acervo
```

Os 36 estão marcados `COUNTRY_REACHED_DISAGREES=true`, com
`COUNTRY_REACHED_OBSERVED` ao lado. **O campo antigo não foi sobrescrito** — ele
foi carimbado pelo lote, e trocá-lo em silêncio mudaria o que 36 cartões afirmam.

> **O PAÍS DO ANÚNCIO NÃO SE DEDUZ DA PASTA ONDE ELE FOI GUARDADO.**

Cada transcrição carrega `SOURCE_COUNTRY` (país do fato), `COLLECTION_COUNTRY`
(onde a coleta rodou), `CASE_COUNTRY` e `SOURCE_LANGUAGE`. Quando a rota não
declarou, é `UNKNOWN` — e continua `UNKNOWN`. **A decisão sobre mostrar 6 falas
francesas e 3 espanholas numa tela italiana é do consumidor, e agora ela é
tomável, porque o fato está preservado.**

---

## 6 · COMO CONSUMIR — SEM MERGE CEGO

**Não faça merge desta branch.** Ela toca `v21_ingest_b.py`, `v21_fechar.py` e
`v21_normalizar.py`, e a sua linhagem tem outra história (as duas não têm
merge-base).

Consuma o **artefato**, como a sua própria §12 já faz:

```bash
git fetch --all --prune

git worktree add --detach /tmp/wt-acervo <HEAD desta branch>
cd /tmp/wt-acervo
bash scripts/v21_cadeia.sh                      # exit 0, ~14 s
python3 scripts/acervo_perda.py                 # exit 0 = contabilidade fecha

cp -r /tmp/wt-acervo/build/ITALY-REALITY-HANDOFF-V2.1 <seu repo>/build/

# e então os três artefatos que o portal lê, como sempre
python3 scripts/site_v21_ingest.py
python3 scripts/meeting_snapshot.py --source-head <HEAD desta branch> --cutoff <...>
python3 scripts/it_casa_dados.py
```

**Confira antes de aceitar** (todos já verdes aqui):

```
mestre                 7847 registros · 0 IDs duplicados
ACERVO_PINNED           947 registros
AINDA_SO_EM_PORTUGUES     0
contratos R2/R3/R4 + geografia   0 violações
ACERVO-TO-PACKAGE-LOSS.json      ACCOUNTING_CLOSES = true
determinismo           duas corridas em árvore limpa, 88 arquivos, byte-idênticas
```

**Ordem sugerida de adoção**, do barato ao caro:

1. **Data dos anúncios** — 414/414, junção sem perda, zero decisão pendente.
   Só exige imprimir `LAST_OBSERVED` junto do selo.
2. **Abstract da ciência** — 81 cartões ganham texto. Exige decidir se mostra
   `PROVED_*` ao lado de `CROP`/`ISSUE`, ou se esconde os 39 `OFF_CASE`.
3. **Os 5 vídeos com fala já citados** — a travessia mínima, 117.304 ch, com
   `SAME_VIDEO_AS_ACTIVITY_ID` pronto.
4. **A família inteira de transcrições** — depois de decidir §5.
5. **`SCIENCE-CORPUS.json`** — 763 registros. Mudança de população: só
   deliberada.

---

## 7 · O QUE ESTA MISSÃO NÃO FEZ

- **`CROP_WINDOWS`** — fora desta rodada por instrução. Continua 29 · PROVED 0 ·
  PARTIAL 2 · UNKNOWN 27, origem não auditável.
- **Portal, UI, `surface-contract`, Opportunity, relevância comercial, Future
  Radar, deploy** — nada tocado.
- **`CROP_IDS` da ciência** — continua do termo da busca. Declarado, não corrigido.
- **`build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip`** — não atualizado. Continua
  a não ser entrada da cadeia, e continua a mentir sobre a sua safra. Decisão do
  dono do repositório, como a sua §10 já registrava.
- **Segunda leitura dos anúncios** — 372 dos 414 têm uma só. Uma segunda coleta
  daria `CHANGE_OBSERVED`. É coleta, não transporte.

---

## 8 · PERDAS QUE RESTAM

| # | PERDA | TAMANHO | DONO | POR QUÊ |
|---|---|---|---|---|
| 1 | 24 falas pedidas sem texto | 24 objetos | coleta | 19 são `HTTP 403 actor-disabled, monthly usage hard limit exceeded` — cota Apify, não ausência de fala |
| 2 | 675 materiais fora de `SCIENCE.json` | 675 · 518.402 ch | **você** | estão em `SCIENCE-CORPUS.json`; adotar é mudança de população |
| 3 | `CROP_IDS` da ciência do termo de busca | 87/88 | **você** | `PROVED_CROP_ID` (47/88) está ao lado |
| 4 | 926 anúncios ES/FR fora do recorte italiano | 926 | recorte | classificados um a um, com o país que a fonte observou |
| 5 | 56 falas sem país do fato · 72 sem língua | — | coleta | a rota não declarou; `UNKNOWN` é o estado correto |
| 6 | `TRANSCRIPT_USED_AS_EVIDENCE` = 0 | 160 falas | **você** | o pacote leva os bytes; usar é do motor |
| 7 | 36 anúncios com país divergente | 36 | **você** | `COUNTRY_REACHED_OBSERVED` diz ES; o campo antigo não foi sobrescrito |
| 8 | 39 papers `OFF_CASE` visíveis como do caso | 39/88 | **você** | `CASE_ADHERENCE` e `PROVED_*` estão no registro |

---

## 9 · ONDE OLHAR

```
data/acervo/ACERVO-SOURCES-V1.json    o endereço imutável de cada insumo
scripts/acervo_fonte.py               resolve e confere SHA256 — levanta, não devolve vazio
scripts/acervo_pinar.py               descobre e pina (FORA da cadeia, roda à mão)
scripts/acervo_transcricoes.py        o censo das falas
scripts/acervo_perda.py               a contabilidade da fronteira (FALHA se não fechar)
scripts/v21_transcricoes.py           escreve TRANSCRIPTS.json
scripts/v21_ciencia_texto.py          abstract + QUERY vs PROVED + SCIENCE-CORPUS.json
scripts/v21_anuncios_prova.py         a data que prova o ATTIVO
tests/test_acervo_refresh.py          18 provas: os 7 cenários de refresh
build/.../ACERVO-TO-PACKAGE-LOSS.json a conta, gravada a cada build
```
