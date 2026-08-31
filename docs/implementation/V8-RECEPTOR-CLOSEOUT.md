# V8 · FECHAMENTO DO CASCO — O PATCH DE UMA LINHA

**Data:** 2026-08-31 · medição executável em `data/implementation/V8-RECEPTOR-CLOSEOUT.json`

```
READ ONLY · NO COLLECTION · NO REAL DATA · NO SUPABASE WIRING
NO DESIGN CHANGE · NO HTML PATCH
```

> Quinta e última medição. Antecessores: index (10), index (11), index (12) e o deploy
> pré-patch. Todos ficam: sem eles não há como mostrar o caminho.

---

## 0 · CUIDADO COM O NOME DO ARQUIVO

O briefing menciona `Formulário e próximos passos(1).zip`. **Esse arquivo não existe.** O
que existe é `Formulário e próximos passos.zip` — **o mesmo caminho de antes, sobrescrito**.

Isso é uma armadilha real: um medidor que confiasse no caminho teria auditado conteúdo
novo achando que era o antigo, ou o contrário. Confirmei pelos bytes:

```
antes ..... 849.123 bytes · 7917564b64a99816cfe0dc3aa671be2e0092c6eb5e2fd2c557a4707766128efc
agora ..... 849.114 bytes · b1256d71708cfaae97b20756c18a67774cf3bdb826bb909404a6222d6f5c925b
```

São exports diferentes. **O caminho mentiu; os bytes não.**

---

## 1 · O CASCO MEDIDO

```
deploy/index.html   372.425 bytes  d28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328
deploy/support.js    69.150 bytes  8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe
deploy/crop-map.js   10.156 bytes  a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8
```

`support.js` e `crop-map.js` têm **SHA idêntico** ao export anterior. Só o `index.html`
mudou, e mudou **+7 bytes** — o tamanho exato de `_ENTITY`.

Guardado em `casco/canonical/deploy-v8-closeout/`, com o `index` gzipado pelo mesmo motivo
da rodada anterior: o antivírus deste ambiente prende o arquivo depois da escrita. Há teste
que descomprime e confere o SHA dos bytes originais.

---

## 2 · O DIFF TEM UMA LINHA

Esta é a prova mais forte desta rodada. Comparando a testemunha anterior com esta, linha a
linha, o arquivo inteiro:

```diff
- FIELD('ENTITY_KIND', 'PERSON_CREATOR | FARM_BUSINESS', 'construcao'), ...
+ FIELD('ENTITY_KIND', 'PERSON_CREATOR | FARM_BUSINESS_ENTITY', 'construcao'), ...
```

**Uma linha removida, uma adicionada. Mais nada.** Nenhuma outra alteração entrou de
carona — e não é preciso confiar na palavra de ninguém: o diff está no artefato e há teste
que reprova se ele crescer.

---

## 3 · O BLOQUEADOR FECHOU

`FIELD_VOICE_ENTITY_KIND_CANONICAL = **PASS**`

```
R-H6-CREATOR       ENTITY_KIND = PERSON_CREATOR | FARM_BUSINESS_ENTITY  ✅
R-H6-FIELD-VOICE   ENTITY_KIND = PERSON_CREATOR | FARM_BUSINESS_ENTITY  ✅
```

Os dois receptores de H6 passaram a falar a mesma língua, e é a do vocabulário canônico
`creator_entity_kind`.

**E `FARM_BUSINESS` abreviado sumiu do casco como valor estrutural** — há teste que varre
o código procurando qualquer `FARM_BUSINESS` que não seja `FARM_BUSINESS_ENTITY`, e não
encontra nenhum. O alias continua existindo onde deve: declarado no `UI_ALIAS_MAP`, como
apelido de tela do index (11).

O resto do contrato do receptor de voz continua inteiro: `HOSE_ID = H6`,
`PARENT_HOSE_ID = H6`, `DISPLAY_LABEL = H6 · CAMPO`, payload `FIELD_VOICE_OBSERVATION`,
`LOAD_STATE = NOT_STARTED`.

---

## 4 · NENHUMA REGRESSÃO

Tudo medido de novo, contra os mesmos critérios:

```
H1..H9 .................................. PASS      HOSES_WITH_COMPLETE_RECEIVER = 9/9
SUBRECEPTOR_HOSE_ID_CANONICAL ........... PASS
DISPLAY_LABEL_SEPARATE .................. PASS
PARENT_HOSE_ID_STRUCTURAL ............... PASS
SOURCE_LANGUAGE_UNKNOWN_GLOBAL .......... PASS
RADAR_CONVERGENCE_PARITY ................ PASS      DEAD_HANDLERS = 0
EVIDENCE_DRAWER_HOSES_COVERED ........... 9/9
ACTION_TYPE_CANONICAL ................... PASS      ACTION_MAP_OBJECT_ID = PASS
TIMELINE_TYPED .......................... PASS      CROP_MAP_GUARD = PASS
GITHUB_PROVENANCE ....................... PASS      SUPABASE_PROVENANCE = PASS
NO_FRONTEND_SECRET ...................... PASS
```

**Nenhum `FAIL` sobrou na medição** — há teste que varre todos os vereditos e reprova se
qualquer um voltar a ser `FAIL`.

A convergência continua derivada e as duas telas continuam concordando: `TERRITORIAL`
independente + `FIELD_HISTORICAL` dependente por `SOURCE_DEPENDENCY` =
**`SINGLE SIGNAL · 1 FAMÍLIA`**.

---

## 5 · UM MEDIDOR SÓ, DE PROPÓSITO

Não escrevi um quinto medidor. O de fechamento **reusa** o da rodada anterior, apontando
para outra testemunha:

```python
from v8_receptor_ready import medir as medir_com
m = medir_com(fontes=abrir(), shas=SHAS)
```

**Dois medidores quase iguais podem divergir** — e a divergência apareceria como *"o casco
melhorou"* quando só o medidor mudou. Há teste que confere que o medidor base aceita a
testemunha por parâmetro, exatamente para impedir que alguém clone.

---

## 6 · RUNTIME SEPARADO, UMA FONTE DE VERDADE

`support.js` é o runtime gerado (`GENERATED from dc-runtime/src/*.ts`). Procurei nele:

```
const receptor · CONV_LEGS · 'EV-0001' · R-H6-FIELD-VOICE
FIELD_VOICE_OBSERVATION · ENTITY_KIND
```

**Nenhum aparece.** A definição de `R-H6-FIELD-VOICE` existe **uma única vez** no pacote
inteiro, no bloco `data-dc-script` do `index.html`. Não há duas fontes de verdade.

---

## 7 · ÓRFÃS

```
ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS ....... 0
OUTPUTS_WITH_ABSENT_RECEPTOR ................ 0
RECEPTORES COM DRIFT DE HELPER .............. 0
```

As quatro classes mantêm exatamente as mesmas contagens de todas as rodadas — **21 / 8 /
5 / 1**. Nada foi reclassificado para chegar a zero, e há teste que reprova se alguma
classe se mover.

A ressalva sobre o zero **continua no arquivo**, reescrita para o fechamento: zero órfã
nunca significou casco pronto por si só — no index (12) esse zero convivia com três
receptores expondo o rótulo no lugar do `HOSE_ID`. O que fecha o casco é a medição dos
receptores. As duas coisas coincidem agora porque as duas foram medidas.

---

## 8 · PROVAS

`tests/test_v8_receptor_closeout.py` — **27 provas**, dentro das
<!--M:TEST_COUNT_CURRENT-->1.007<!--/M--> da suíte, 0 falhas. As 786 anteriores preservadas.

Incluem: o diff de uma linha, os 7 bytes, o SHA idêntico de `support.js` e `crop-map.js`, a
ausência de `FARM_BUSINESS` abreviado, a fonte única de verdade e o medidor não duplicado.

---

## 9 · SAÍDA

```
CASCO_WITNESS = casco/canonical/deploy-v8-closeout/
                deploy-index.html.gz · support.js · crop-map.js · vercel.json
SHA256_INDEX  = d28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328
SHA256_ZIP    = b1256d71708cfaae97b20756c18a67774cf3bdb826bb909404a6222d6f5c925b

FIELD_VOICE_ENTITY_KIND_CANONICAL = PASS

H1 = PASS   H2 = PASS   H3 = PASS   H4 = PASS   H5 = PASS
H6 = PASS   H7 = PASS   H8 = PASS   H9 = PASS

HOSES_WITH_COMPLETE_RECEIVER = 9/9

SUBRECEPTOR_HOSE_ID_CANONICAL  = PASS
DISPLAY_LABEL_SEPARATE         = PASS
PARENT_HOSE_ID_STRUCTURAL      = PASS
SOURCE_LANGUAGE_UNKNOWN_GLOBAL = PASS

RADAR_CONVERGENCE_PARITY = PASS
DEAD_HANDLERS = 0
EVIDENCE_DRAWER_HOSES_COVERED = 9/9

ACTION_TYPE_CANONICAL = PASS
ACTION_MAP_OBJECT_ID  = PASS
TIMELINE_TYPED        = PASS
CROP_MAP_GUARD        = PASS

GITHUB_PROVENANCE   = PASS
SUPABASE_PROVENANCE = PASS

SUPPORT_JS_DUPLICATE_RECEPTOR_LOGIC = NO

ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS = 0
OUTPUTS_WITH_ABSENT_RECEPTOR          = 0

TESTS_TOTAL = 813      TESTS_FAILED = 0

DESIGN_PATCH_REQUIRED = NO

CASCO_RECEPTOR_READY = YES

READY_TO_CREATE_SUPABASE_INSTANCE_SCHEMA = YES
READY_FOR_FIRST_SHADOW_LOAD = NO
READY_TO_WIRE_REAL_DATA     = NO
```

### `EXACT_BLOCKERS`

```
nenhum no casco.
```

---

## 10 · O QUE AINDA SEGURA O WIRING — E NÃO É O CASCO

`CASCO_RECEPTOR_READY = YES` fecha **o casco**. Não fecha a ligação. O que falta agora é de
outra natureza, e já estava declarado antes desta rodada:

```
1  o commit de H2 é uma BRANCH, não um SHA fixo
   registrado como SOURCE_COMMIT = RESOLVER_ANTES_DA_CARGA

2  a migration é rascunho — MIGRATION_APPLIED = NO, e exige revisão humana

3  não existe instância Supabase: nada foi exercido contra um banco real

4  o corpo das views e RPCs não foi escrito — só as assinaturas

5  as políticas de RLS estão desenhadas, não implementadas
```

**Nenhum dos cinco é responsabilidade do Claude Design.** O casco terminou o trabalho dele.
