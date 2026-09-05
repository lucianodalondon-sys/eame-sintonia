# RECONCILIAÇÃO DO LOTE ITALIANO QUE JÁ ESTÁ NO SUPABASE

`COUNTRY = IT` · `SOURCE_ID = IT-ADAMA-CATALOG` · `COLLECTION_ID = IT-ADAMA-CATALOG-2026-08-30`
· `RULE_VERSION = IT-RECONCILE-1.0` · `RECONCILED_AT = 2026-09-05`

> **Esta missão para na porta da Inteligência.** Ela não classifica relevância, não roteia
> para capacidade, não abre o Casco, não define política do D1 e não ativa o Passaporte.

---

## 1 · A PERGUNTA

Há **195 objetos** sob o prefixo `IT/adama-website` no bucket `raw`. Eles subiram em
2026-08-30, pelo runner local, e o portão de preservação fechou com as oito condições
satisfeitas: 195 presentes, 195 hashes conferidos **depois de baixar cada um de volta**,
zero divergência, 80.714.570 bytes conferidos remotamente.

A pergunta desta missão não é *"o que esse material deveria virar"*. É:

> **de cada um dos 195, o que a casa já sabe — e quanto disso já foi pago?**

---

## 2 · A ROTA BARATA: LER A PROVA, NÃO O BALDE

Este ambiente **não tem** `SUPABASE_URL` nem `SUPABASE_SECRET_KEY`, e não deve ter. A rota
até o balde já havia sido tentada e registrada como fechada aqui, em
`LABEL-MANIFEST.json`:

| rota tentada | resultado medido |
|---|---|
| `ADAMA_MEDIA_DOWNLOAD` (adama.com) | **403** — três amostras, o mesmo veredicto |
| `MINISTERO_BANCA_DATI_ETICHETTE` | cadeia TLS incompleta (só a folha) |
| `SUPABASE_BUCKET` | **`NO_CREDENTIALS_IN_THIS_ENVIRONMENT`** |

E o inventário dos 195 **já existe em Git**, com SHA256 conferido no retorno. Abrir o balde
não acrescentaria um fato e custaria uma credencial que este ambiente não deve carregar.
Por isso a reconciliação é derivada de **prova preservada**, e o script fixa cada fonte pelo
**SHA do blob** — branch anda, conteúdo não.

`scripts/it_supabase_reconciliar.py` · `python3 scripts/it_supabase_reconciliar.py --conferir`

---

## 3 · O QUE ENTRA COMO IDENTIDADE, E O QUE NÃO ENTRA

| chave | força | por quê |
|---|---|---|
| `SHA256` | **forte** | o conteúdo é o próprio nome |
| `OBJETO` | **forte** | o endereço no balde |
| `ARQUIVO_LOCAL` | **forte** | o caminho no acervo que subiu |
| `SOURCE_URL` | **forte** | a rota de mídia daquele documento |
| `PRODUCT_URL` | fraca | identifica o **produto pai**, nunca o documento |
| `ORIGINAL_FILENAME` | fraca | colide — `robots.txt` casa com 42 arquivos do acervo |

Foi essa separação que evitou o erro mais fácil desta reconciliação: **139 documentos
aparecem no portal italiano** — mas por `PRODUCT_URL`. O que está no portal é o produto
pai. Nenhum daqueles PDFs foi lido.

### As três leis do crosswalk

1. **Mencionado não é consumido.** `ALREADY_CONSUMED` exige **duas** provas citadas: o
   conteúdo foi lido **e** virou fato derivado.
2. **Chave fraca não estabelece identidade.** Ela entra como contexto e nunca como prova.
3. **Ausência declarada é resultado.** `UNKNOWN` nunca é promovido a estado.

---

## 4 · OS SEIS BALDES — DISJUNTOS, ORDENADOS, FECHANDO EM 195

| balde | n | o que sustenta |
|---|---:|---|
| `ALREADY_CONSUMED` | **53** | 51 páginas de produto lidas e viradas em fato (`ACTIVE_INGREDIENT`, `FORMULATION`, `PACKAGE_SIZE`, crosswalk contra o registro) + 2 PDFs cujos bytes a casa leu pela rota Ministero |
| `KNOWN_NOT_CONSUMED` | **137** | contados no acervo e declarados **não lidos com motivo**: `PARSE_STATE = NOT_PARSED`, `PARSE_BLOCKER = "PDF preservado fora deste ambiente; adama.com devolve 403 aqui"` |
| `ALREADY_ACCOUNTED` | **3** | papel declarado e consumidor nomeado: `indice-captura.json` e `enumeracao.json` alimentam `adama_it_preservar.py`/`adama_it_catalogo.py`; `robots.txt` é a testemunha de `ROBOTS_DISALLOWS_AJAX_ROUTE` |
| `SUPABASE_ONLY` | **2** | `home-italia-it.html` e `sitemap-italia-it.xml`: fora do balde, só a prova de preservação os conhece |
| `AMBIGUOUS` | **0** | — |
| `UNKNOWN` | **0** | — |
| **TOTAL_ACCOUNTED** | **195** | |

### O achado que muda o valor do balde

Dos 195, **142 nunca tiveram o conteúdo lido** — e a razão está escrita, não suposta: a
origem devolve 403, e o material original vive numa máquina residencial fora do Git.

> **O balde deixou de ser cópia de segurança e passou a ser a única rota viva até esse
> conteúdo.** Os 137 documentos estão lá, com SHA256 conferido, prontos para leitura — e
> ninguém precisa pedir nada à `adama.com` de novo.

Isso é o oposto de "falta coletar". **Não falta coletar nada.** Falta ler o que já foi pago.

---

## 5 · A PENEIRA TÉCNICA — A PRIMEIRA PERGUNTA NÃO É RELEVÂNCIA

| veredicto | n | motivo |
|---|---:|---|
| `KEEP` | **53** | já é fato na casa |
| `DEFER` | **142** | *não utilizável **ainda*** — o conteúdo não é alcançável **neste ambiente**; a próxima ação é ler **a partir do balde** |
| `REJECT_WITH_REASON` | **0** | nada foi julgado inutilizável |
| `ERROR` | **0** | nenhum objeto sem bytes conferidos |

`REJECT = 0` **é um resultado, não uma omissão.** Os dois objetos que compartilham os
mesmos bytes (`Postscript 80 XL` e `Davai`, mesma Scheda di Sicurezza) não são duplicata a
descartar: a casa já decidiu que *hash igual não apaga origem*, e as duas procedências
continuam inteiras. **A máquina nunca rejeita por ausência.**

Dos 137 em `DEFER`, **9** carregam `CONTENT_READABLE = false` — esses recebem motivo
próprio (`CONTENT_DECLARED_UNREADABLE`) e uma próxima ação diferente: reler do balde e, se
o texto não sair, **declarar a rota de texto fechada** para aquele documento. Não rejeitar.

---

## 6 · PRÉ-PASSAPORTE SOMBRA — O QUE ELE É, E O QUE ELE NÃO É

`data/samples/IT-SUPABASE-COLETA/IT-195-PRE-PASSAPORTE-SOMBRA.json`

**Sombra** quer dizer: usa o vocabulário fechado de `PASSPORT-1.0` e **não é passaporte**.
Nenhum evento foi selado, nenhum portão foi atravessado, `data/passaporte/EVENTOS.jsonl`
não foi tocado. É a projeção que o Passaporte **teria** se estes 195 entrassem — para que o
dia da entrada seja uma **migração declarada**, e não uma digitação.

Três decisões ficam **abertas e escritas**, em vez de resolvidas por conveniência:

- `SOURCE_FAMILY`: `MANUFACTURER_PUBLIC_CATALOG` **não existe** no vocabulário fechado de
  `PASSPORT-1.0`. Ou a família entra, ou o lote é dobrado numa família existente.
- **Granularidade**: 195 passaportes por objeto, ou um `DATASET_SNAPSHOT` com
  `UNIT_COUNT = 195`.
- `CONSUMPTION_STATE` dos 53 já consumidos: **qual** capacidade consumiu, e por **qual caso
  publicado**. Sem isso o selo seria digitado, não derivado — então ele fica `PENDING`, que
  é a verdade.

---

## 7 · CONTROL_PLANE_EVIDENCE_CANDIDATE

`data/samples/IT-SUPABASE-COLETA/CONTROL-PLANE-EVIDENCE-CANDIDATE.json`

**Não é o Control Plane de Coleta.** Não é estado canônico, não define schema e não abre
missão. É o que a casa **já escreveu** sobre esta coleta — onde ela parou, o que falhou,
qual rota morreu, quando foi, quanto pesou — preservado com a prova ao lado, para que o dia
em que o Control Plane existir não comece com uma página em branco.

Cada candidato traz `KIND`, `VALUE`, `SCOPE`, `RELIABILITY` (`MEDIDO` · `DECLARADO` ·
`INFERIDO`) e a citação da fonte.

---

## 8 · O CHECKPOINT ANTES DA FASE CARA

```
TOTAL                         = 195
MECHANICALLY_RECONCILED       = 190
ALREADY_READ                  =  53
READ_QUEUE                    =   5      (os 3 CAPTURE + 2 MANIFEST, casos de borda)
PERCENT_REQUIRING_NEW_READING = 2,6 %
```

O portão passou, e por um motivo que precisa ficar escrito: **a fila de leitura é baixa
porque a casa já tinha feito o trabalho** — não porque o crosswalk foi permissivo.
`REUSED_EXISTING_WORK = 190`.

E há um número que não é escolha, é medição:

```
OBJECT_BYTES_AVAILABLE_IN_THIS_ENVIRONMENT = 0
ACTUALLY_READ_NOW                          = 0
```

**Nenhum byte dos 195 existe neste ambiente.** `data/raw` está fora do Git por política
(D-003) e não há credencial do balde aqui. Toda leitura registrada nesta reconciliação é
leitura de **prova**, nunca de objeto — e o artefato diz isso em vez de deixar a contagem
sugerir o contrário.

---

## 9 · O QUE NÃO MUDOU

```
SUPABASE_CHANGED     = NÃO      (nenhuma chamada; não há credencial aqui)
STORAGE_CHANGED      = NÃO
CANONICAL_CHANGED    = NÃO      (sintonia/canonical intocada)
INTELLIGENCE_CHANGED = NÃO
PORTAL_CHANGED       = NÃO
OS_43_CHANGED        = NÃO
MOTOR_CHANGED        = NÃO
PASSAPORTE_ATIVADO   = NÃO
D1_POLICY_DEFINED    = NÃO
scripts/voz.py       = intocado
```

---

## 10 · O QUE FICA NA PORTA DA INTELIGÊNCIA

`COLLECTION_PACKAGE_STATE = READY`, com **uma** coisa faltando, e ela é pequena:

> **ler os 137 documentos a partir do balde.**

Eles estão lá, com hash conferido, e a rota da origem está morta. Essa leitura é uma
missão da linha da Itália — não desta. Esta aqui para aqui.
