# CATÁLOGO ADAMA ESPAÑA → ACERVO EAME · integração seletiva, e os dois motivos de parar

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-collection-es` · **Base:** `300e6b7`
**Handoff usado:** `claude/adama-es-local-browser` @ **`0ed66f2`** — mais novo que o `6040ab6`
que a coordenação conhecia, e a diferença importou.

**Produção não foi tocada.** Nenhuma migration aplicada, nenhum import executado, nenhum
secret usado, handoff não mesclado.

---

## VEREDITO

```
ADAMA_ES_CATALOG_INTEGRATION = PARTIAL_WITH_EXACT_REASON
```

Tudo o que podia ser provado em banco descartável foi provado, e passa. A produção não
foi tocada por **dois motivos medidos**, nenhum deles resolvível deste ambiente:

**1 · A importação do catálogo tem um pré-requisito que não existe.**
As 52 linhas `ROPF_ONLY` do crosswalk afirmam *"este registro está no ROPF e não estava no
catálogo que lemos"*. Elas não têm lado de produto, e a trava
`crosswalk_tem_pelo_menos_um_lado` recusa linha sem nenhum dos dois lados. Sem
`registro_regulatorio` povoado com os 96 registros vigentes do ROPF, o import **para na
primeira delas** — medido, não suposto.

E a importação do registro regulatório **não existe em lugar nenhum**: nem nesta branch,
nem na do handoff. Ela é outra importação, com gate próprio, e `ES-CASE-001` continua
ABERTA. Construí-la por conta própria sob uma autorização que diz *"catálogo"* seria
alargar escopo por julgamento meu, e por isso não construí.

**2 · `PRESENÇA NO INVENTÁRIO ≠ BYTES CONFERIDOS`.**
O commit `0ed66f2` traz uma ressalva que o `6040ab6` não tinha, e ela desmonta o número
que eu publiquei na rodada passada. Dos 196 assets:

| | |
|---|---|
| presentes no inventário remoto | **196** |
| com `sha256` reconferido por download+hash e prova em artefato | **11** |
| com prova **apenas de presença** | **185** |
| que **nunca** tiveram o conteúdo conferido | **1** — `media 2981`, `TOPIC Folleto Diptico.pdf` |

E o 2981 é justamente o que recebeu **HTTP 520** — que é quando gravação parcial é
plausível. Objeto presente com bytes truncados passaria por preservado.

Eu escrevi `PRESERVADOS_E_VERIFICADOS = 196` porque foi o que a mensagem do operador dizia.
O artefato do handoff diz outra coisa, e o artefato vence. É o mesmo erro de duas rodadas
atrás — publicar ZERO onde a resposta era NÃO MEDIDO — virado do avesso: publicar
VERIFICADO onde a resposta era PRESENTE.

O remédio existe, tem nome, é só leitura e não gasta nada:
`py scripts/storage_preservar.py --diagnosticar --verificar-tudo`.

---

## C · O que foi integrado, e D · o que ficou de fora

Integração **seletiva**. Não houve merge.

| categoria | arquivo | por quê |
|---|---|---|
| **A · migration** | `supabase/migrations/014_catalogo_publico_fabricante.sql` | renumerada de 010; único conteúdo alterado |
| **B · import** | `supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql` | **regenerado**, não copiado |
| **B · gerador** | `scripts/catalogo_importar.py` | adaptado ao schema de hoje |
| **C · consultas** | `supabase/consultas/ADAMA-ES-CATALOGO-14-PERGUNTAS.sql` | perguntas de controle |
| **C · regressões** | `supabase/tests/regressoes_catalogo_es.sql` | novo: 33 afirmações, red team incluído |
| **D · artefatos** | `ADAMA-ES-PRODUCT-INTELLIGENCE`, `…-CONFIRMACAO-REGULATORIA-DO-PAR`, `ES-MAPA-VOCABULARIO-IDS`, `…-PRESERVACAO-{PLANO,RELATORIO,DIAGNOSTICO}`, `…-DOCUMENTOS-MANIFEST` | entradas do gerador e prova da preservação |
| **E · NÃO integrado** | `storage_preservar.py`, `recolher_lote.sh`, `adama_es.py`, `adama_crosswalk.py`, `adama_intelligence.py`, `adama_es_*.py`, `test_adama_es.py`, `test_roundtrip_catalogo.py`, fixtures de HTML, workflow `adama-es-censo.yml`, docs de coleta local | são a máquina do operador: coleta por navegador e envio ao Storage. Há teste que reprova se subirem — é assim que se mede que não houve merge |
| **F · já absorvido** | `008`, `009`, docs de piloto e apresentação | o core evoluiu por cima; nada re-puxado |

## E · A migration 014

Nasceu como `010` quando o core tinha 9 migrations. O core seguiu e ocupou 010–012 com o
calendário; o **014 ficou vago de propósito desde a 015**, esperando por ela. A reserva
cumpriu a função.

`HANDOFF_SCHEMA_VALID_THEN ≠ SCHEMA_VALID_NOW` — reconferida antes de entrar:
15 tabelas `catalogo_*`, **zero colisão de nome**, e os cinco donos que ela referencia
(`collection_run`, `raw_asset`, `registro_regulatorio`, `crop`, `issue`) existem e não
mudaram de forma entre a 013 e a 018.

**Ordem provada:** `001–007 · 009 · 010–012 · 013 · 014 · 015 · 016 · 017 · 018 · 008`.
A 014 não precisou pular migration nenhuma.

## F · `DUPLICATE_OWNERS_CREATED = 0`, e as três correções que isso exigiu

**1 · O id do MAPA não tem mais casa dentro de `crop`.**
O gerador resolvia `crop_id` por `crop.mapa_id_cultivo`. Essa coluna **não existe**: a 009
a removeu, e disse por quê — *"`mapa_id_cultivo` era seed espanhol dentro da entidade
canônica; OLIVE é OLIVE nos três países"*. Recriá-la para o import rodar seria desfazer a
isolação de país por conveniência de importação. O dono existe: `crop_local` /
`issue_local`, com `(pais, source_system, external_id)`. O gerador passou a resolver por
lá. A lei `NO_FUZZY_SILENT_MATCH` não mudou — sem casar, fica NULL e o rótulo publicado
permanece.

**2 · Duas tabelas do catálogo não tinham chave natural.**
O teste de idempotência pegou: o segundo import levava as janelas de 3 para 6 e o
crosswalk de **108 para 216** — com os 44 `LOCAL_REGISTERED` virando **88** e os 12
não-provados virando 24. Números de gate dobrando porque um arquivo rodou duas vezes. A
014 ganhou as duas chaves e o gerador, os `ON CONFLICT` correspondentes. Como a 014 nunca
foi aplicada em lugar nenhum, o conserto é nela — não numa 019.

**3 · O "não provado" podia carregar prova.**
O red team virou um `MATCHED_EXACT` em `ADAMA_SITE_ONLY` e **o banco aceitou**: nada dizia
que *"presente só no site da ADAMA"* significa que nenhum registro foi encontrado. Uma
linha podia afirmar não-provado e exibir o número do registro ao lado. Nova trava:
`site_only_nao_carrega_registro`.

## G · Fresh DB · H · Idempotência

Banco montado do zero, 17 migrations, fixture, quatro ensaios, o pré-requisito e o import.
**Três execuções do mesmo import, contadores idênticos.** `IDEMPOTENT IMPORT ≠ DELETE AND
RECREATE`: 1709 INSERTs, **todos** com `ON CONFLICT … DO NOTHING`, zero `UPDATE`, zero
`DELETE`, zero `TRUNCATE`, zero `DO UPDATE`.

E o import é determinístico: gerado duas vezes da mesma entrada, **idêntico byte a byte**.
Ele difere do arquivo histórico do handoff, e deve — aquele foi gerado quando nada estava
preservado (`raw_asset: NENHUM`); agora há 138.

## L–Q · Contadores esperados × medidos

| | esperado | medido |
|---|---|---|
| produtos | 56 | **56** |
| documentos | 147 | **147** |
| relações de cultivo | 711 | **711** |
| — declaradas | 588 | **588** |
| — citadas | 123 | **123** |
| usos com CROP + ISSUE | 5 | **5** |
| crop × dose sem issue | 26 | **26** |
| janelas de aplicação | 3 | **3** |
| `LOCAL_REGISTERED` | 44 | **44** (41 exatos + 3 por evidência) |
| `LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED` | 12 | **12** |

Nenhum dos 12 virou `NOT_REGISTERED` — e o estado **nem existe** no vocabulário.

## R · S · Round-trip de evidência

Os doze casos A–L resolvem em banco descartável. `DB ROW → proveniência → captura → RAW →
evidência`, com o caminho de volta existindo em cada um.

O **AVASTEL** entrou com `158.083.718 bytes` declarados — o caso-limite dos 50 MB, agora
com o tamanho no banco. O que **não** foi feito é o §17 na produção: `download → SHA match`
exige credencial de Supabase, que este ambiente não tem.

## T · Isolação de país

Os 56 produtos são todos `ES`. Consulta `IT` e consulta `FR` devolvem zero do catálogo
espanhol, e `f_crop_calendar('IT')` continua vazia depois do import. Regressão obrigatória,
cumprida.

## U · CUPROXI FLO · V · NEPTUNE · W · `ES-CASE-001`

**CUPROXI FLO continua com dois identificadores tipados distintos:** `19232` no produto do
catálogo, `ES-00979` no registro, ligados por `MATCHED_WITH_EVIDENCE` — *"nome comercial
idêntico + composição compatível"*. **Não fundidos.** O `TRICUPROXI F` fica como
`ADAMA_SITE_ONLY`, sem registro correspondente.

**NEPTUNE** é `ES-00211` e entrou com os três documentos, todos com RAW.
`PRESERVED_PDF ≠ CASE_RESOLVED`: **`ES-CASE-001` permanece ABERTA.** A importação organiza
evidência; não fabrica veredito.

## X · Red team e mutações

As quinze tentativas viraram afirmações e recusas executáveis. Duas derrubaram algo real —
a trava que faltava no `ADAMA_SITE_ONLY`, e a idempotência ausente. Uma terceira derrubou
um teste **meu**: o helper `recusa_por` que escrevi em rodadas anteriores **não desfazia**
um comando que passava, e aqui um passou, virou 41 linhas e envenenou os contadores da
própria suíte. Corrigido nas quatro suítes que o usam: o comando agora roda numa
subtransação que é sempre desfeita.

```
192 afirmações SQL do zero  (45 · 19 · 33 · 21 · 41 · 33)   0 falhas
 23 mutações                todas pegaram · 0 erros
648 testes Python           verdes
```

## I · Gates de pré-produção, refeitos

```
CATALOG_IMPORT_ENGINEERING_GATE   READY
EAME_COLLECTION_ENTRY_GATE        READY
RAW_PRESERVATION_GATE             CLOSED   ← presença
RAW_CONTENT_VERIFIED_GATE         OPEN     ← 11/196 reconferidos, 1 nunca conferido
IMPORT_CAN_BE_NEXT_MISSION        YES
```

## J · K · Produção

**Nenhuma migration aplicada. Nenhum import executado.** O caminho canônico existe e está
identificado — `supabase-migrate.yml`, `workflow_dispatch`, secrets em Actions — e não foi
acionado, pelos dois motivos do topo.

Uma observação para quem for acioná-lo: o pré-voo desse workflow só autoriza escrever num
banco com **0, 23, 26 ou 30** tabelas em `public`. O core hoje tem mais, e o workflow ainda
aplica apenas *001–007 e 009–012*. Ele precisa ser estendido antes de qualquer produção —
e isso é mudança de caminho de produção, não de importação.

## O que a próxima missão precisa, na ordem

1. `--diagnosticar --verificar-tudo` na máquina do operador → fecha `RAW_CONTENT_VERIFIED_GATE`.
2. A **importação do registro regulatório ES** (96 fichas vigentes do ROPF), com gate
   próprio. Existe um ensaio que a simula em banco descartável —
   `supabase/ensaios/ES-ROPF-PRE-REQUISITO-DO-CATALOGO.sql` — e ele **não é** essa
   importação nem pode virar ela.
3. Estender `supabase-migrate.yml` para 013–018 + 014 e para a contagem de tabelas atual.
4. Só então a importação do catálogo em produção, que já está provada em banco descartável.
