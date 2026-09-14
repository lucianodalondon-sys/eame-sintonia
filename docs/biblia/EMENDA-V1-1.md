# EMENDA CONSTITUCIONAL V1 → V1.1 — apêndice E da Bíblia

**Data:** 2026-09-07 · **HEAD antes:** `72838db` · **Ramo:** `claude/biblia-canonica-da-coleta`

> A COL-LAW-069 manda que nenhuma lei mude em silêncio, e que toda mudança registre
> `LAW_ID · BEFORE · AFTER · WHY · EVIDENCE · IMPACT · VERSION`. Este ficheiro é esse
> registro.

```
VERSION BEFORE   V1     48 leis
VERSION AFTER    V1.1   78 leis   (+30)
LEIS APAGADAS    0
LEIS RENUMERADAS 0
```

---

## AS DUAS EMENDAS

| # | nome | parte nova | leis |
|---|---|---|---|
| **1** | **A PLACA DE VÍDEO** — o System Map é a camada oficial de observabilidade visual | PARTE XVI | `COL-LAW-101` … `112` (12) |
| **2** | **AS LEIS ROUBADAS** — o que sistemas maduros de coleta já aprenderam | PARTE XVII | `COL-LAW-201` … `218` (18) |

**Por que dois blocos de numeração novos, e não continuar de 070.** Na V1 o número
`COL-LAW-NNN` correspondia à secção `NNN` da missão fundacional que criou a lei. Manter essa
rastreabilidade vale mais que uma sequência contínua: `1xx` é a emenda da observabilidade,
`2xx` é a emenda pós-pesquisa. Nenhum número da V1 mudou.

---

## AS 12 LEIS DA OBSERVABILIDADE

| LAW_ID | nome | ORIGEM | IT |
|---|---|---|---|
| `COL-LAW-101` | Tudo deve ser renderizável | `ARCHITECTURAL_DECISION` | `PARTIAL` |
| `COL-LAW-102` | As quatro verdades: `DECLARED` · `CODE` · `OBSERVED` · `BIBLE` | `ARCHITECTURAL_DECISION` | `PARTIAL` |
| `COL-LAW-103` | Estado derivável não se escreve à mão | `EXISTING_SINTONIA_LAW` | `PARTIAL` |
| `COL-LAW-104` | Contrato de componente renderizável | `ARCHITECTURAL_DECISION` | `PARTIAL` |
| `COL-LAW-105` | Contrato de conexão renderizável | `CONSOLIDATED_FROM_MULTIPLE` | `PARTIAL` |
| `COL-LAW-106` | Contrato de corrida renderizável | `CONSOLIDATED_FROM_MULTIPLE` | `PARTIAL` |
| `COL-LAW-107` | A perda tem de aparecer na aresta | `ARCHITECTURAL_DECISION` | `ABSENT` |
| `COL-LAW-108` | Quatro vistas, uma verdade só | `ARCHITECTURAL_DECISION` | `PARTIAL` |
| `COL-LAW-109` | Níveis de zoom; layout não governa arquitetura | `ARCHITECTURAL_DECISION` | `IMPLEMENTED` |
| `COL-LAW-110` | Observabilidade por nascimento | `ARCHITECTURAL_DECISION` | `IMPLEMENTED` |
| `COL-LAW-111` | A camada de observabilidade não é uma segunda verdade | `ENGINEERING_PRINCIPLE` | `IMPLEMENTED` |
| `COL-LAW-112` | Toda afirmação do mapa tem evidência navegável | `EXISTING_SINTONIA_LAW` | `PARTIAL` |

## AS 18 LEIS ROUBADAS

| LAW_ID | nome | roubada de | IT |
|---|---|---|---|
| `COL-LAW-201` | **Artefato não é fato** | FollowTheMoney · OpenSanctions | `PARTIAL` |
| `COL-LAW-202` | O modelo `ARTIFACT → CLAIM` | FollowTheMoney | `ABSENT` |
| `COL-LAW-203` | A procedência chega até o valor | Nomenklatura | `PARTIAL` |
| `COL-LAW-204` | Dedupe não destrói a história | OpenSanctions | `PARTIAL` |
| `COL-LAW-205` | A fonte é estável; o endpoint é substituível | Memorious · Aleph | `PARTIAL` |
| `COL-LAW-206` | Três identidades, e a URL não é uma delas | Crossref · OpenAlex | `PARTIAL` |
| `COL-LAW-207` | Descobrir ≠ buscar ≠ derivar | Memorious · Scrapy · Crawlee | `ABSENT` |
| `COL-LAW-208` | O Source Registry é a memória da coleta | consolidado | `PARTIAL` |
| `COL-LAW-209` | A corrida é história, e história não se reescreve | OpenLineage | `ABSENT` |
| `COL-LAW-210` | A corrida só fica `COMPLETE` no fim | Scrapy · Browsertrix | `PARTIAL` |
| `COL-LAW-211` | A configuração da corrida fica congelada | OpenLineage | `PARTIAL` |
| `COL-LAW-212` | O incremental fecha a janela antes de entrar (*watermark*) | GDELT · Media Cloud · OpenAIRE | `ABSENT` |
| `COL-LAW-213` | Incremental não é só somar | consolidado | `ABSENT` |
| `COL-LAW-214` | Zero tem semântica | consolidado | `PARTIAL` |
| `COL-LAW-215` | Fail loud — o nosso bug não vira `UNKNOWN` do mundo | Scrapy · Crawlee | `PARTIAL` |
| `COL-LAW-216` | Três eixos de confiança | OpenSanctions · OpenCTI | `PARTIAL` |
| `COL-LAW-217` | `FIRST_SEEN` e `LAST_SEEN` são do SINTONIA | OpenSanctions | `ABSENT` |
| `COL-LAW-218` | Bulk não é API pontual | OpenAlex · OpenAIRE · Crossref · Common Crawl | `NOT_APPLICABLE` |

**Nenhuma plataforma foi instalada.** Não há OpenLineage, Kafka, Grafana, Prometheus,
Temporal, OpenCTI, Browsertrix, FollowTheMoney nem qualquer outra no repositório. Foram
roubadas as leis.

---

## O QUE NÃO VIROU LEI NOVA — 6 emendas absorvidas

> **Controle de complexidade.** Depois de cada emenda a pergunta foi: *isto resolve um
> problema real do SINTONIA que uma lei existente já não resolve?* Seis vezes a resposta foi
> **não**, e criar uma lei nova teria produzido duas leis para a mesma pergunta — exatamente
> o que a Bíblia proíbe.

| emenda do briefing | absorvida por | por quê |
|---|---|---|
| E28 · geografia: artefato ≠ fato | **COL-LAW-032** (+ COL-LAW-201, que diz de quem é cada campo) | a lei da geografia já separava `SOURCE_LOCATION` de `FACT_LOCATION` e `COUNTRY_SCOPE`; faltava só dizer o **dono**, e isso é a 201 |
| E29 · `RAW` / `METADATA` / `TEXT` separados | **COL-LAW-007** | já formaliza `PDF_RAW ≠ PDF_TEXT`, `HTML_RAW ≠ EXTRACTED_ARTICLE`. `METADATA` é mais um derivado, não uma lei nova |
| E34 · edge explícita; proximidade não cria relação | **COL-LAW-048** (+ citada em 105) | é literalmente a lei existente. Repeti-la criaria a segunda verdade |
| E35 · `CAN DO ≠ DID DO` | **COL-LAW-049** + **COL-LAW-102** | a 049 já tinha `DECLARED/CODE/OBSERVED`; a 102 acrescentou a quarta (`BIBLE`) em vez de duplicar |
| E36 · `OBSERVED` exige prova de RUN | **COL-LAW-102** + **COL-LAW-112** | é a definição de `OBSERVED` e a regra de evidência navegável; não precisa de artigo próprio |
| E39 · o mapa mostra a saúde da fonte | **COL-LAW-028** + **COL-LAW-104** | a 028 define os estados; a 104 obriga o componente a expor `HEALTH`, `LAST_RUN`, `LAST_ERROR`. A soma já é a regra |

**Superseded:** nenhuma. **Merged:** nenhuma lei da V1 foi fundida noutra — seis emendas
**do briefing** foram absorvidas, o que é diferente.

---

## AS LEIS DA V1 QUE FICARAM MAIS FORTES

Estas **não mudaram de texto**; ganharam uma lei que as completa. Está anotado no corpo de
cada uma.

| lei da V1 | o que a V1.1 acrescentou |
|---|---|
| `COL-LAW-031` temporalidade | a matriz completa de 7 tempos com dono (`COL-LAW-217`), e **de quem é o `FACT_TIME`** (`COL-LAW-201`) |
| `COL-LAW-032` geografia | de quem é o `FACT_LOCATION` (`COL-LAW-201`) |
| `COL-LAW-028` saúde da fonte | os outros dois eixos de confiança (`COL-LAW-216`) |
| `COL-LAW-049` declared/code/observed | a quarta verdade, `BIBLE` (`COL-LAW-102`) |
| `COL-LAW-023` reconciliação | a perda visível na aresta (`COL-LAW-107`) |
| `COL-LAW-024` zero inesperado | as três palavras do zero (`COL-LAW-214`) |
| `COL-LAW-030` mundo ≠ pipeline | o carimbo das versões na corrida (`COL-LAW-211`) |
| `COL-LAW-018` rota mais barata capaz | descobrir barato antes de buscar caro (`COL-LAW-207`) |

---

## IMPACTO NA MATRIZ DA ITÁLIA

| | V1 | V1.1 |
|---|---:|---:|
| leis medidas | 48 | **78** |
| `IMPLEMENTED` | 21 | **24** |
| `PARTIAL` | 23 | **42** |
| `ABSENT` | 4 | **11** |
| `NOT_APPLICABLE` | 0 | **1** |
| `UNKNOWN` | 0 | **0** |

**O número de `ABSENT` subiu de 4 para 11, e isso é uma boa notícia.** Não é a Itália que
piorou — é a régua que ficou maior. Sete coisas que antes nem eram medidas passaram a ter
nome, e uma lacuna com nome é uma lacuna que alguém pode fechar.

`NOT_APPLICABLE` entra como estado novo na matriz (COL-LAW-218: ciência não está no perfil
italiano de hoje). **Não se marca `ABSENT` uma lei que não se aplica** — seria dívida
inventada.

---

## UM DEFEITO ENCONTRADO NO CAMINHO — REGISTRADO, NÃO CONSERTADO

**`tem_teste` procura a aresta do teste no sentido errado.**

`system-map/scripts/generate_system_map.py:1825`:

```python
tem_teste = any(l["from"] == "C-TESTES" or l["from"] == "C-MAPA-TESTES" for l in ent)
```

Quando um teste **lê** um ficheiro, o dado vai do ficheiro para o teste, e o scanner mede
`C-BIBLIA → C-TESTES (READS)`. A aresta existe e está certa; ela só não está na **entrada**
da peça testada, está na **saída**. Resultado: uma peça com teste real fica 🟡 com a
mensagem *«é uma lei sem prova executável apontando para ela»* — e há uma
(`tests/test_biblia.py`, 28 testes, no CI).

É exatamente a avaria que o próprio ficheiro descreve no comentário de `prova_do_tipo`:

> *«Enquanto estas regras não acompanharam, o mapa dizia "Apify: biblioteca que ninguém
> importa" sobre uma peça com NOVE ligações de import. Uma regra escrita para a direção
> antiga produz um status errado com a mesma cara de um status certo — e essa é a pior
> avaria que este ficheiro pode ter.»*

O mesmo conserto foi feito para `IMPORTS` e não foi feito para `READS`.

**Alcance medido:** 29 peças ganhariam `tem_teste`; **26 já são verdes por outra via**, e só
**3 mudariam de cor** — `C-BIBLIA`, `C-AS-FONTES` e `C-LASTMILE`, todas hoje 🟡.

**Por que não foi consertado aqui.** A missão manda registrar problema funcional e **não
corrigir no embalo**, e este é runtime do mapa. Consertá-lo repintaria duas peças que esta
missão não examinou — e pintar de verde uma peça que ninguém leu é precisamente o que a lei
do carimbo proíbe.

> **Consequência aceita:** `C-BIBLIA` fica 🟡 `PENDING`. Isso é **honesto** — a régua de
> hoje diz isso —, e não foi torcido para ficar verde. Entra como gap **G-29**.

---

## O QUE ESTA EMENDA NÃO FEZ

Nada disto foi implementado, e o mapa **não** desenha nenhum deles como `CURRENT`:
extração de claim · *statement store* · *repair runner* · motor de *watermark* ·
*change data capture* · propagação de deleção · *scoring* de fonte · *scoring* de rota ·
dedupe de ciência · OpenLineage · FollowTheMoney · OpenCTI · Browsertrix · snapshots bulk ·
UI nova.

Nenhum coletor, workflow, orquestrador, executor, admissão, banco ou pipeline de produção
foi alterado funcionalmente.
