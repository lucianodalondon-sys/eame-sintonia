# A MEDIÇÃO DA REGRA DE T2 — e por que ela não foi escrita

> **Pergunta da missão:** *o que um documento precisa provar para a Admission
> dizer que ele pertence a «T2 — Clima e tempo»?*
>
> **Resposta medida:** com o material que esta casa tem hoje, **não se sabe**.
> Uma regra que separa o gabarito EXISTE — e ela separa por **dia da semana e
> nome de departamento**. Treinada num publicador, acerta **0 de 10** no
> publicador que não viu.
>
> ```
> T2_RULE_IMPLEMENTED = NO
> ```
>
> `PERGUNTAS_DO_UNIVERSO` ficou exactamente como estava.

Quem quiser refazer a medição corre isto, e não precisa de acreditar em
ninguém:

```bash
py provas/a_regra_de_t2.py
py -m unittest tests.test_a_regra_de_t2
```

---

## 1 · O QUE JÁ ERA CANÔNICO ANTES DESTA MISSÃO

`T2 = Clima e tempo` **não foi inventado aqui**. Está declarado em
`system-map/data/sources.generated.json`, bloco `MASTER_ITALIANO`, com cinco
fontes e os seus tópicos:

| fonte | publicador | tópicos declarados |
|---|---|---|
| `IT-T2-001` | ARPAE | precipitação, temperatura, água no solo, agroclima |
| `IT-T2-002` | ARPAV | chuva, temperatura, evapotranspiração, alerta agroclimático |
| `IT-T2-003` | CNR-IBE | seca, SPI/SPEI, mapas |
| `IT-T2-004` | SIAS Sicília | chuva, temperatura, seca, território |
| `IT-T2-005` | ALSIA | agrometeorologia, estações |

```
T2_MEANING_ALREADY_CANONICAL = YES
```

---

## 2 · O GABARITO — 46 documentos reais, nenhum inventado

Cada linha tem `ITEM · EXPECTED · WHY · EVIDENCE` em
`provas/a_regra_de_t2.py`. O rótulo vem do que **o próprio documento declara nas
suas primeiras linhas** — evidência que qualquer pessoa abre e confere.

```
POSITIVOS_T2   10   (ARPAV Agrometeo ×4 · ARPAE Settimanale ×2 ·
                     Bollettino Agrometeorologico Regionale ×1 ·
                     Meteo Veneto ×2 · SIAS ×1)
NEGATIVOS_T2   33   (fitossanitários, regulatórios, de mercado)
CASOS_AMBIGUOS  3   (ARIF Puglia — ficam NAO_SEI, e não viram número)
```

### O contraexemplo que funda tudo

**A ARPAV está dos dois lados do gabarito.** A mesma agência publica:

- `Meteo Veneto: luglio 2026 molto caldo, poche piogge` → **T2**
- `U.O. Fitosanitario — Bollettino n. 20 VITE` → **T3**

    O PUBLICADOR NÃO DECIDE O TERRITÓRIO.

Sem estes seis negativos da ARPAV, classificar pela fonte **pareceria
funcionar** — e estaria errado em silêncio.

### Os três ambíguos não foram arredondados

O `Notiziario_Agrometeorologico` da ARIF Puglia abre com duas páginas de análise
sinóptica (saccature, Groenlândia, promontório subtropical) e **só depois** traz
mosca e *Bactrocera*. A ficha `IT-T3-008` declara `T3` — e declara, nos seus
próprios tópicos, **`agrometeorologia`**.

É as duas coisas num só PDF. Não se resolve com o material desta árvore, e o
brief autorizou que ficasse `NAO_SEI`. **Não virou SIM nem NÃO para o número dar
melhor.**

---

## 3 · O VOCABULÁRIO REAL — contado, não suposto

| termo | T2 (10) | NÃO-T2 (33) |
|---|---:|---:|
| `evapotraspirazione` | 6 | 0 |
| `climatologia` | 7 | 2 |
| `bagnatura fogliare` | 5 | 2 |
| `agrometeo` | 8 | 8 |
| `temperatura` | 7 | 11 |
| `previsione` | 0 | 11 |
| `meteo` | 9 | 25 |
| `vento` | 7 | 30 |
| `clima` | 9 | 21 |

    NENHUM termo aparece nos 10 positivos e em ZERO negativos.

E o resultado que ninguém esperava: **as palavras óbvias de clima aparecem MAIS
fora de T2 do que dentro.** `vento` está em 30 dos 33 negativos e em 7 dos 10
positivos. Não é acidente — é o que um boletim de praga **é**: a praga responde
ao tempo, e por isso todo o boletim fitossanitário fala de tempo.

    DOCUMENTO SOBRE CLIMA ≠ DOCUMENTO QUE APENAS MENCIONA CLIMA,
    E O VOCABULÁRIO SOZINHO NÃO VÊ A DIFERENÇA.

As duas palavras que mais parecem servir traem-se quando se lê onde estão:

- `climatologia` aparece nos boletins de VITE da ARPAV porque eles creditam o
  *«Servizio Meteorologia e Climatologia di Arpav»*. **É o nome de quem
  colaborou, não o assunto.**
- `bagnatura fogliare` aparece nos boletins da Campânia como **condição de risco
  de infecção** — é vocabulário de defesa da cultura, não de clima.

---

## 4 · OS TRÊS DESENHOS

### Desenho A · lista plana de palavras — o único mecanismo que existe

`admissao._do_universo` faz `if achadas: return SIM` na **primeira** palavra que
casa. É isso que há, e a missão proibiu mudar a lógica da Admission.

| candidata | TP | TN | FP | FN | UNKNOWN | ambíguo forçado |
|---|---:|---:|---:|---:|---:|---:|
| `A1-obvia` | 9 | 1 | **32** | 0 | 1 | 3 |
| `A2-agro` | 8 | 25 | 8 | 1 | 1 | 3 |
| `A3-medida-forte` | 7 | 29 | 4 | 2 | 1 | 3 |
| `A4-so-a-mais-forte` | 6 | 33 | 0 | 3 | 1 | 3 |
| `A5-titulo-do-documento` | 9 | 33 | 0 | 0 | 1 | 3 |

A melhor, `A5`, parece boa e **não é uma regra de clima**: é a lista dos **nomes
comerciais** de três publicações (`agrometeo… informa`, `meteo veneto`,
`bollettino agrometeorologico`). E mesmo assim responde `NAO_SEI` ao **SIAS** —
uma fonte T2 declarada, cuja página é uma tabela de precipitação sem uma linha
de prosa.

### Desenho B · grupos de sinais — não medível aqui

Exigir *N* sinais de grupos distintos obriga a **contar**, e `_do_universo`
**pára na primeira palavra**. Implementar B é mudar a lógica da Admission.
Proibido na missão.

### Desenho C · prova da fonte — não medível, e errado

`_do_universo` só lê `('texto','title','nome','topics','crops','resumo')` —
nunca `source_id`. E, sobretudo: **a ARPAV publica T2 e T3**. C erraria seis
documentos deste gabarito por construção, com ar de quem tem prova. Além disso
quebraria `DECLARADO ≠ OBSERVADO`: a porta passaria a dizer *«é T2 porque a
ARPAV publicou»*, nunca *«é T2 porque o documento prova»*.

---

## 5 · O ATAQUE QUE DECIDIU A MISSÃO

Comparar candidatas que **eu** escolhi só responde *«estas não servem»*. A
pergunta dura é: **existe alguma lista de palavras que sirva?**

Então deixou de haver candidatas minhas. O corpus propôs **6.582** termos e
bigramas dos positivos; ficaram **4.942** que não aparecem em nenhum dos 33
negativos; e **todos** os 10 positivos são alcançáveis por algum deles.

**Existe.** Uma lista que separa este gabarito na perfeição existe. A pergunta
seguinte é a única que importa: **de que é que ela é feita?**

```
7/10  'venerdì'                      7/10  'dipartimento'
7/10  'unità organizzativa'          7/10  'pomeriggio'
7/10  'territorio unità'             7/10  'per sicurezza'
7/10  'organizzativa meteorologia'   7/10  'sicurezza del'
```

Dias da semana. Horas do dia. O nome do departamento que imprime.

    NÃO É VOCABULÁRIO DE CLIMA. É A IMPRESSÃO DIGITAL DE QUEM IMPRIME.

E a prova final — treinar num publicador e testar noutro:

| treina sem | regra que o ajuste produz | cobre o treino | acerta no retido |
|---|---|---:|---:|
| SIAS | `venerdì`, `zone montane` | 9/9 | **0/1** |
| ARPAE | `unità organizzativa`, `width class` | 8/8 | **0/2** |
| ARPAV | `cumulate` | 3/3 | **0/7** |

```
GENERALIZACAO = 0/10
```

Cobre o treino **sempre**. Acerta no retido **nunca**.

    UMA REGRA QUE SÓ ACERTA EM QUEM JÁ VIU NÃO É UMA REGRA:
    É A LISTA DOS DOCUMENTOS QUE JÁ TÍNHAMOS.

---

## 6 · O PORTÃO

| condição | valor |
|---|---|
| `T2_MEANING_ALREADY_CANONICAL` | **YES** |
| `REAL_POSITIVE_EXAMPLES_EXIST` | **YES** — 10, de 3 publicadores |
| `REAL_NEGATIVE_EXAMPLES_EXIST` | **YES** — 33, incluindo 6 do mesmo publicador de positivos |
| `RULE_CAN_DISTINGUISH_T2_FROM_T3` | **NO** — generalização 0/10 |
| `RULE_CAN_DISTINGUISH_T2_FROM_T7` | **NÃO CHEGOU A SER PERGUNTADO** |
| `NO_NEW_ARCHITECTURAL_LAW_REQUIRED` | **NO** |

```
PORTAO = FECHADO
T2_RULE_IMPLEMENTED = NO
```

A quarta condição fechou o portão, e as seguintes não se responderam: dar um
número a uma regra que não existe seria fabricar precisão.

A sexta condição merece nome. Para separar *«documento SOBRE clima»* de
*«documento que MENCIONA clima»* faltam **duas** coisas que esta casa não tem:

1. uma **lei** que diga o que é ser *sobre* um assunto — e ela não existe;
2. um **mecanismo** que conte sinais em vez de parar na primeira palavra.

As duas mudam a Admission. A missão proibiu as duas.

---

## 7 · O QUE A PORTA RESPONDE HOJE, E POR QUE ISSO ESTÁ CERTO

Sem regra escrita, `_do_universo` devolve:

```
NAO_SE_APLICA  «não há regra escrita do que conta como «T2».
                Sem regra, esta porta não inventa uma.»
```

Isto **não é uma falha a corrigir**. É a porta a dizer a verdade sobre si
mesma. O erro seria o contrário: escrever `A1-obvia`, ver 9 de 10 positivos
virarem `SIM`, publicar o número — e não contar que **32 dos 33 negativos**
viraram `SIM` junto.

---

## 8 · O QUE SE DESCOBRIU E NÃO ERA A PERGUNTA

Coisas medidas por acidente, registadas porque se perdem se não forem escritas.
**Nenhuma foi corrigida nesta missão** — o brief mandou não atacar o próximo
bloqueio.

- **`lancio` casa dentro de `bilancio`.** As listas existentes procuram
  subcadeias, sem fronteira de palavra. Por isso o `Bilancio Fitosanitario` é
  reclamado por **T9** (*«lançamento»*), e `eventi intensi` — um evento
  meteorológico — é reclamado por T9 via `evento`. Isto faz documentos T2
  legítimos receberem `NAO` com uma justificação falsa.
- **Um documento pode pertencer a dois territórios.** O `decidir(item,
  universo)` é por par, portanto o modelo aguenta — mas o gabarito da casa e as
  fichas das fontes assumem **um território por fonte**, e a ARIF Puglia prova
  que isso não é verdade do documento.
- **Território é propriedade da FONTE; universo é pergunta ao DOCUMENTO.** São
  duas coisas diferentes com o mesmo nome, e a ARPAV mostra-as a divergir.

---

## 9 · O QUE ISTO CUSTARIA SE FOSSE IGNORADO

O caminho fácil estava a um `commit` de distância: escrever

```python
"T2": ["clima", "tempo", "meteo", "temperatura", "pioggia", "vento"],
```

ver `TP = 9/10` e declarar T2 resolvido. O que esse commit teria feito, medido:

```
FALSE_POSITIVE = 32 dos 33 negativos
```

Todos os boletins fitossanitários de Campânia, Lazio, Trentino, Molise,
Piemonte, Puglia e Veneto passariam a ser **clima**. E como a Admission escreve
no `LIVRO-DE-DECISOES.json`, cada um deles ficaria lá **com justificação** —
*«fala de clima, tempo, meteo, temperatura — que é do que «T2» trata»* — que é
verdade palavra a palavra e falsa como julgamento.

    O PIOR DEFEITO NÃO É O QUE FALHA ALTO.
    É O QUE ACERTA NA MÉTRICA E ERRA NO MUNDO, COM A PROVA ESCRITA AO LADO.
