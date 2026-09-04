# Red team semântico dos cinco vãos — a evidência sustenta a conclusão?

```
SEMANTIC_RED_TEAM = PASS
```

A pergunta desta rodada não foi «o código rodou?». Os cinco vãos da coleta
dirigida tinham rodado todos: cinco perguntas, cinco respostas, `EXIT 0`. A
pergunta foi outra, e mais dura:

    A EVIDÊNCIA REALMENTE SUSTENTA A CONCLUSÃO QUE O MOTOR PRODUZIU?

E a primeira coisa que ela encontrou não foi um estado errado. Foi uma **razão
errada ao lado de um estado certo** — que é pior, porque ninguém audita a razão.

> `OPP_75C37DED9160`, macieira × carpocapsa, Veneto.
> `WINDOW_OPEN_NOW = UNKNOWN` — **correto**.
> `WINDOW_OPEN_NOW_METHOD = CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS` — **falso**.
> O Bollettino frutticolo n.25 de 03/09/2026 declara a medição em letras:
> «**terzo volo terminato**».

    UM CARTÃO QUE ACERTA O ESTADO E MENTE A RAZÃO ENSINA A NÃO LER A RAZÃO.

Este documento é o relatório dos dez itens que a missão pediu. Tudo o que ele
afirma sai de `python3 scripts/v21_red_team_semantico.py` (grava
`data/samples/AUDITORIA-SOMBRA/V115-RED-TEAM-SEMANTICO.json`) e de
`python3 scripts/v21_regressao_do_red_team.py`.

---

## 0 · A travessia que prova a prova

Um red team que passa na primeira execução prova pouco: pode estar a medir o que
já estava certo. Então o código **anterior** — `4b97cf5`, via `git show` para um
diretório de rascunho — foi posto de volta em memória e recebeu as mesmas
orações reais do acervo.

```
$ python3 scripts/v21_regressao_do_red_team.py
ANTES = 4b97cf5   ·   DEPOIS = arvore de trabalho

── voo relatado vira janela?
   antes  : ['PEST_STAGE_WINDOW']
   depois : []
── razao do UNKNOWN
   antes  : ('UNKNOWN', 'CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS')
   depois : ('NO', 'FONTE_DECLARA_A_FASE_DA_PRAGA_COMO_ENCERRADA')
── fase conclusa abre?
   antes  : ('YES', 'FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE')
   depois : ('NO', 'FONTE_DECLARA_A_FASE_COMO_ENCERRADA')
── prosa qualitativa distingue-se do silencio?
   antes  : NAO
   depois : SIM

REGRESSAO_DO_RED_TEAM = PASS
```

Quatro defeitos, todos reproduzidos no código de ontem e todos fechados hoje.

    UM TESTE QUE NÃO REPROVA A VERSÃO ANTIGA NÃO ESTÁ A TESTAR NADA.

---

## 1 · Emilia-Romagna · os 5% estão ultrapassados agora?

```
CLASSIFICAÇÃO = UNKNOWN
```

Não `NO`. `NO` exigiria evidência de que 5% **não** foi atingido, e ninguém a
tem. O Consorzio Fitosanitario de Reggio Emilia, em 03/09/2026, declara a
soglia e declara que «il quadro rimane tendenzialmente buono» — que é prosa
sobre o território, não medição de parcela.

| | |
|---|---|
| `WINDOW_TYPE` | `THRESHOLD_WINDOW` |
| `WINDOW_DEFINED` | `YES` — a regra dos 5% está declarada |
| `WINDOW_OPEN_NOW` | `UNKNOWN` |
| método | `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE` |
| `THRESHOLD_STATE` | `NOT_DECLARED` |
| `STATUS` | `VALIDATE_NOW` · `COMMERCIAL_PRIORITY = SALES_READY` |

O método mudou de nome e a mudança é a correção: `CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS`
acusava o nosso acervo; `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE`
descreve o documento. São afirmações diferentes sobre o mundo.

**Nenhum número foi inferido.** O red team verifica, no pacote, que nenhum
registro de apoio do par declara percentagem medida — e se algum declarasse e o
motor não a tivesse lido, ele quebraria.

> ⚠️ **Item aberto nomeado.** A frase «il quadro rimane tendenzialmente buono»
> está no registro `IT-COL-2609-RE-TIGNOLETTA`, mas **não** é atribuída ao par:
> a oração não nomeia a tignoletta, e a lei do repositório exige o alvo escrito
> no texto. Por isso `THRESHOLD_STATE` fica `NOT_DECLARED` e não
> `QUALITATIVE_PICTURE_ONLY`. Não abri a lei da atribuição para fechar este
> campo: seria a mesma inferência por proximidade que a missão 4 fechou. A
> guarda existe, está pinada em `T49`/`T50`, e dispara no dia em que a oração
> nomear o alvo.

---

## 2 · Veneto · fim do voo é fim da necessidade?

**Não.** E o motor confundia as duas coisas — não no estado, mas na frase.

O boletim diz três coisas na mesma respiração, e o motor empilhava as três numa
resposta só:

```
FASE DA PRAGA    «terzo volo terminato»                        → terminou
RECOMENDAÇÃO     «continuare la difesa con prodotti larvicidi» → continuar
JANELA           (ninguém disse qual condição define o momento)
```

    FIM DO VOO NÃO É FIM DA NECESSIDADE DE INTERVENÇÃO.
    E RECOMENDAR CONTINUAR NÃO É DECLARAR JANELA ABERTA.

Agora são quatro respostas com quatro donos:

| campo | valor | dono |
|---|---|---|
| `PEST_STAGE_STATE` | `STAGE_ENDED` | `IT-COL-2609-VN-CARPOCAPSA` |
| `ACTION_RECOMMENDATION_STATE` | `CONTINUE_RECOMMENDED` | `IT-COL-2609-VN-CARPOCAPSA` |
| `WINDOW_DEFINED` | `NO` | — |
| `WINDOW_OPEN_NOW` | `UNKNOWN` | — |

**Por que «continuare la difesa» não constitui janela aberta.** Porque é
*direção*, e a direção já tem dono: `NEED_DIRECTION = POSITIVE_PRESSURE`. Deixar
a mesma frase provar também a janela seria um elo a provar dois — exatamente o
que o item 4 proíbe. O que a recomendação faz, e faz sozinha, é impedir que o
fim do voo seja lido como fim da campanha: ela viaja no cartão, com trecho e
identificador, ao lado da fase encerrada.

**E a janela desapareceu — de propósito.** `\bvolo\b` sozinho virava
`PEST_STAGE_WINDOW`. Mas «terzo volo terminato, danni in aumento» **relata o
inseto**; não manda tratar no voo. É a mesma lei que a fenologia já tinha desde
a V1.1.3:

    O ESTÁDIO É O ESTADO DA PLANTA. O VOO É O ESTADO DA PRAGA.
    A JANELA É O ESTADO AMARRADO A UMA AÇÃO.

`PEST_STAGE_WINDOW` passa a exigir o verbo de ação e o substantivo de estádio na
mesma oração — «intervenire in corrispondenza delle ovideposizioni» é janela;
«terzo volo terminato» não é.

---

## 3 · Friuli-Venezia Giulia · a fonte parou de publicar

```
CLASSIFICAÇÃO = UNKNOWN
```

O último boletim de milho do ERSA é o n.15 de 12/08/2026; o n.16 é de cereais de
outono-inverno. A série fechou para a temporada. Isso responde **uma** coisa e
só uma: não há medição nova.

| | |
|---|---|
| `WINDOW_OPEN_NOW` | `UNKNOWN` |
| `THRESHOLD_STATE` | `NOT_DECLARED` |
| registro novo criado | **nenhum** |

    SÉRIE FECHADA NÃO É LIMIAR NÃO ULTRAPASSADO. É AUSÊNCIA DE MEDIÇÃO.

O red team verifica que **nenhum** registro `IT-COL-2609-FVG-*` foi criado.
Inventar um seria o único jeito de mudar o estado, e não se faz.

---

## 4 · Toscana · quantos elos uma frase pode provar?

**Um.** A frase «Siamo nella fase di maggior suscettibilità a questa malattia»
prova `JANELA_ABERTA_AGORA`, e mais nada.

| elo | dono | fato | tipo |
|---|---|---|---|
| `SINAL_ATUAL` | `IT-PHEN-040` | `2026-09-03` | declarado |
| `DIRECAO_POSITIVA` | `IT-PHEN-040` | `POSITIVE_PRESSURE` | declarado |
| `JANELA_DEFINIDA` | `IT-COL-2609-TO-BOTRITE` | `PHENOLOGY_WINDOW` | declarado |
| `JANELA_ABERTA_AGORA` | `IT-COL-2609-TO-BOTRITE` | `FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE` | declarado |
| `VINCULO_COM_PORTFOLIO` | `IT-LBL-*` (rótulo ministerial) | `VERIFIED_LABEL_MATCH` | declarado |
| `TEMPO_PARA_ACAO` | janela + direção | janela aberta agora **e** documento corrente | **derivado declarado** |

A direção vem de um documento (o boletim de Siena de 27/08); a janela vem de
outro (o de 03/09). O vínculo com o portfólio vem do rótulo ministerial, que não
é boletim nenhum. `T53` quebra se a evidência da janela ou da direção aparecer
também como prova do produto em qualquer `ACT_NOW` do pacote.

`TEMPO_PARA_ACAO` **é** derivado dos outros dois, e está marcado como derivado.
Isso não é um elo a esconder-se: `ACTION_CHAIN_REQUIRES` publica a regra no
próprio cartão — «a condição está aberta agora e o documento que o diz é
corrente». Derivação declarada é auditável; derivação silenciosa é que não.

    CADA ELO COM DONO SEPARADO. E O QUE É DERIVADO DIZ QUE É DERIVADO.

`STATUS = ACT_NOW`, `WHY_NOW_CODES = ['CADEIA_COMPLETA']`.

---

## 5 · Umbria · 10–15% é da Umbria

| | |
|---|---|
| regra no cartão | «soglia de intervencao de **10-15%** de cachos com ovos e/ou larvas» |
| evidência da janela | `IT-COL-2609-UM-TIGNOLETTA` |
| evidência da janela na Emilia-Romagna | `IT-PHEN-001` — **outra** |
| `NEED_DIRECTION` | `NO_ACTION_RECOMMENDED` |
| `STATUS` | `WATCH` · `COMMERCIAL_PRIORITY = TO_VALIDATE` |

Os 5% da Emilia-Romagna não viajaram: `janela_tipada` filtra por região desde a
missão 4, e as duas regiões usam evidências diferentes. E a fonte da Umbria diz
«in generale non sono necessari interventi» — a porta fecha, e `WATCH` é a
resposta certa, não uma falha da coleta.

> Uma nota sobre o teste que faz esta verificação: procurar a substring `5%` na
> condição da Umbria **acusa a Umbria à toa**, porque «10-15%» contém «5%». O
> red team usa `(?<![\d-])5\s?%`.
>
>     O TESTE QUE CONFUNDE «15%» COM «5%» É O MESMO ERRO QUE ELE PROCURA.

---

## 6 · As testemunhas negativas

Cinco frases que um dia vão aparecer num boletim e que **nunca** podem virar
resposta a uma condição medida. Cada uma esteve perto de virar.

| frase | o que ela quase respondeu | o que responde agora |
|---|---|---|
| «la situazione buona in tutta la provincia» | limiar satisfeito | `UNKNOWN` |
| «il quadro rimane tendenzialmente buono» | limiar **não** satisfeito | `UNKNOWN` |
| «pressione contenuta nella maggior parte dei vigneti» | limiar não satisfeito | `UNKNOWN` |
| «siamo nella fase conclusa della difesa» | **janela ABERTA** | `NO` |
| «danni presenti nei frutteti» | pressão que abre janela | `UNKNOWN` |

    FRASE QUALITATIVA SÓ RESPONDE A UMA CONDIÇÃO QUANTITATIVA QUANDO A PRÓPRIA
    FONTE DECLARA A EQUIVALÊNCIA. NUNCA POR LEITURA NOSSA.

A quarta era um buraco real: o padrão de presente lia «siamo nella fase» e não
lia «conclusa» — a frase que **fecha** a janela abria-a. Fechado, e a regressão
prova que o código de ontem a abria.

E uma distinção que não existia: **a fonte falar em prosa e a fonte calar davam
a mesma frase no cartão**. Agora `FRASE_QUALITATIVA_NAO_RESPONDE_CONDICAO_QUANTITATIVA`
e `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE` são respostas diferentes.

---

## 7 · O acervo relido inteiro

`ANTES` = `V21-7285e903bfb1c147`, gerado repondo os módulos de `4b97cf5` e
rodando `bash scripts/v21_cadeia.sh` — não de lembrança. `DEPOIS` = a árvore de
trabalho. O caso é arquétipo × cultura × alvo × região, nunca o hash.

**43 casos antes, 43 depois. 5 mudaram — e 4 deles só na razão.**

| caso | o que mudou |
|---|---|
| macieira × carpocapsa · Veneto | `WINDOW_TYPE` `PEST_STAGE_WINDOW` → `None`; `WINDOW_DEFINED` `YES` → `NO`; `WHY_NOW_CODES` ganha `SEM_JANELA_DEFINIDA` |
| videira × tignoletta · Emilia-Romagna | só o método |
| videira × tignoletta · Umbria | só o método |
| milho × piralide · Friuli | só o método |
| tomate × peronospora · Veneto | só o método |

`STATUS`, `COMMERCIAL_PRIORITY` e `EXTERNAL_MATERIAL_READY` **não mudaram em
nenhum dos 43**. Nenhum número subiu.

```
STATUS                   TO_VALIDATE 9 · WATCH 22 · FUTURE_PREPARATION 7
                         VALIDATE_NOW 3 · ACT_NOW 2
COMMERCIAL_PRIORITY      STRATEGIC_OPPORTUNITY 8 · TO_VALIDATE 17
                         COMMERCIAL_WATCH 13 · SALES_READY 5
EXTERNAL_MATERIAL_READY  NO 38 · YES 5

WINDOW_DEFINED           NO 37 · YES 6          (antes: NO 36 · YES 7)
WINDOW_OPEN_NOW          UNKNOWN 41 · YES 2     (igual)
WINDOW_RULE_STATE        RULE_NOT_DECLARED 36 · RULE_DECLARED 6
                         RULE_DELEGATED_TO_FARM 1                 (campo novo)
PEST_STAGE_STATE         STAGE_NOT_DECLARED 40 · DECLINING 1
                         ENDED 1 · PEAK 1                         (campo novo)
ACTION_RECOMMENDATION    NOT_DECLARED 29 · START 5 · NOT_NEEDED 3
                         CONCLUDED 2 · PROHIBITED 2 · SUSPEND 1
                         CONTINUE 1                               (campo novo)
```

`CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS` desapareceu do pacote — `T51` quebra se
voltar.

---

## 8 · Os casos sem regra de janela, e a primeira coleta dirigida

`python3 scripts/v21_regras_de_janela_ausentes.py` grava a tabela em
`data/samples/AUDITORIA-SOMBRA/V115-REGRAS-DE-JANELA-AUSENTES.json`, ordenada
por **defensabilidade comercial** — não por facilidade da fonte.

    A TABELA VEM ANTES DA COLETA. QUEM COLETA SEM A PERGUNTA ESCRITA VOLTA COM
    O QUE ENCONTROU, NÃO COM O QUE PRECISAVA.

> Sobre o número: a missão fala em **12**. A medição de `JANELA-AGRONOMICA-E-
> REPROCESSAMENTO.md` era anterior ao piloto dos cinco vãos; antes desta rodada
> o pacote tinha **11**, e a macieira × carpocapsa do Veneto entrou ao perder a
> janela falsa — voltando a 12. Depois da coleta abaixo são **11 +
> 1 delegada**.

### O item 1 · macieira × carpocapsa · Veneto — coletado

A única linha `SALES_READY` da tabela, com dois produtos do catálogo e direção
que manda agir. Pergunta escrita antes:

> **QUAL REGRA AGRONÔMICA DEFINE QUANDO AGIR contra carpocapsa em macieira no
> Veneto?**

Fonte: **Regione del Veneto, U.O. Fitosanitario — «Manuale difesa integrata del
melo», revisione n. 1, marzo 2020**. Entrou pela porta real da coleta
(`build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json`, família
`CURRENT_FIELD_SIGNALS`) como `IT-COL-2609-VN-REGRA-CARPOCAPSA`.

**A resposta não foi a que se esperava, e é melhor do que a esperada:**

> «Per cui le decisioni devono essere necessariamente basate sulle osservazioni
> aziendali e sulla situazione storica dell'azienda.»

A Regione publica as gerações (primeiro voo em meados de abril, segundo no fim
de junho, terceiro na primeira década de agosto), publica o monitoramento, e
declara **risco elevado** para a empresa com dano à colheita superior a 2% no
ano anterior — mas **não fixa gatilho regional**. Ela delega ao pomar.

    «NÃO ACHAMOS A REGRA» E «A REGRA MANDA O POMAR DECIDIR» SÃO RESPOSTAS
    DIFERENTES. UMA PEDE MAIS COLETA; A OUTRA FECHA A PERGUNTA.

Chamar isto de `WINDOW_RULE_MISSING` seria a mesma mentira pequena do item 2:
acusar a fonte de não ter dito o que ela disse com todas as letras. Então o
cartão passa a dizer:

| | |
|---|---|
| `WINDOW_RULE_STATE` | `RULE_DELEGATED_TO_FARM` |
| `WINDOW_RULE_EVIDENCE_ID` | `IT-COL-2609-VN-REGRA-CARPOCAPSA` |
| `WHAT_IS_MISSING` | `WINDOW_RULE_DELEGATED_TO_FARM` (não mais `WINDOW_RULE_MISSING`) |
| Market Development | `VALIDATE_AT_FARM_LEVEL` · `REGRA_DELEGADA_AO_POMAR` |
| Technical & Scientific | `CONFIRM_AT_FARM_LEVEL` · `REGRA_DELEGADA_AO_POMAR` |
| `NEXT_TRIGGER` | «a observação do próprio pomar — a regra regional declara que a decisão é da empresa, e por isso não há gatilho regional para esperar» |

Mandar Market Development «definir a condição regional» era mandá-lo procurar um
documento que a Regione já disse que não vai publicar.

### E o documento de regra trouxe um defeito com ele

`aberta_agora` sempre teve o ramo `DOCUMENTO_NAO_CORRENTE` — e ele **nunca era
alcançado**, porque `janelas_do_sinal` passava `corrente = True` a todos. No
acervo de hoje isso não fazia diferença: as 16 candidatas saem todas de
documentos com 22 dias ou menos. Mas um manual de 2020 diria «a condição está
satisfeita agora» com a mesma cara de um boletim de ontem.

    UM MANUAL DIZ QUAL É A REGRA. SÓ UM BOLETIM DIZ COMO ESTÁ O CAMPO HOJE.
    A REGRA NÃO ENVELHECE; O ESTADO ENVELHECE EM DIAS.

`WINDOW_DEFINED` continua `YES` para o manual — a regra é a regra. O que a data
governa é só a segunda pergunta. Medido: **zero candidatas mudaram** ao ligar a
guarda. `T54` e `T57` seguram.

### As 11 linhas que não foram coletadas, e por quê

| # | par | região | prioridade | direção | por que ficou |
|---|---|---|---|---|---|
| 1 | videira × peronospora | Friuli | `TO_VALIDATE` | `NEUTRAL_MENTION` | próximo lote — 2 produtos, porta não fechada |
| 2 | videira × peronospora | Umbria | `TO_VALIDATE` | `NO_ACTION_RECOMMENDED` | a fonte manda parar |
| 3 | videira × peronospora | Emilia-Romagna | `TO_VALIDATE` | `WINDOW_CONCLUDED` | a fonte manda parar |
| 4 | videira × Scaphoideus | Umbria | `TO_VALIDATE` | `NEUTRAL_MENTION` | fonte é **ato administrativo** — nunca vira janela agronômica sozinho |
| 5 | arroz × Echinochloa | Itália | `TO_VALIDATE` | `UNKNOWN` | direção não lida; a coleta certa é de direção, não de janela |
| 6 | milho × piralide | Lombardia | `TO_VALIDATE` | `TREATMENT_PROHIBITED` | proibição vigente |
| 7 | videira × Scaphoideus | Toscana | `TO_VALIDATE` | `WINDOW_CONCLUDED` | ato administrativo + porta fechada |
| 8 | milho × diabrótica | Lombardia | `TO_VALIDATE` | `TREATMENT_PROHIBITED` | proibição vigente |
| 9–11 | videira × oídio | Friuli, Umbria, Toscana | `TO_VALIDATE` | vários | **sem produto do catálogo** no par |

**Nenhuma coleta indiscriminada foi aberta.** A pergunta exata de cada linha
está escrita no artefato, pronta para o próximo lote.

---

## 9 · QA do ISTAT — a trilha separada

```
QA_PASS = PARTIAL     2024 = YES · 2025 = YES · 2026 = UNKNOWN
CARIMBO = NÃO APLICADO
```

`python3 scripts/v21_qa_do_istat.py` executa a revisão que o carimbo exigiria —
URL, dataset, unidade, valor positivo, fórmula declarada nos derivados, chave
não duplicada, unidade estável por indicador, e o fechamento aritmético
`produção ÷ 10 ÷ área = rendimento` a 2%. **2 945 linhas, zero falhas.**

E mesmo assim 2026 responde `UNKNOWN`: são 939 linhas que o próprio ISTAT
publica como estimativa provisória (`OBSERVATION_CLASS = OUTLOOK`).

    CARIMBAR SEM TESTEMUNHA É OPINIÃO COM CARA DE PROCESSO.
    E CARIMBAR PROVISÓRIO COMO DEFINITIVO É ERRAR EM SILÊNCIO SEIS MESES DEPOIS.

**O carimbo não foi aplicado, e o custo dele está medido:** tornaria **2 006
linhas** client-safe e tiraria `OFFICIAL_AREA_NOT_CLIENT_SAFE` de **43 cartões**
— quer dizer, mudaria a camada comercial de todo o pacote. Isso é uma segunda
mudança, com o seu próprio antes-e-depois, e é decisão de vocês, não efeito
colateral de um red team. `T58` pina o veredito e pina que nada foi carimbado.

Nenhuma linha ISTAT foi recoletada.

---

## 10 · O que passou a segurar isto

| teste | o que fixa |
|---|---|
| `T46` | relato de voo não é janela; ação amarrada ao estádio é |
| `T47` | a fase da praga tem dono e não é a colheita |
| `T48` | «continuar a defesa» é recomendação, não janela |
| `T49` | as cinco frases qualitativas nunca abrem condição medida |
| `T50` | prosa qualitativa ≠ silêncio; «fase conclusa» não abre |
| `T51` | nenhum cartão acusa falta de medição que a fonte declarou |
| `T52` | 10–15% é da Umbria, 5% é da Emilia-Romagna |
| `T53` | cada elo de um `ACT_NOW` com dono separado |
| `T54` | os 30 dias são os mesmos em dois módulos; documento velho não fala do agora |
| `T55` | regra que delega não é regra ausente |
| `T56` | regra delegada não manda ninguém procurar o que não existe |
| `T57` | nenhuma janela aberta vem de documento não corrente |
| `T58` | o QA do ISTAT separa definitivo de provisório, e não carimba |

Suíte: **758 descobertos · 739 executados · 6 falhas · 2 erros · 14 pulados** —
as mesmas 8 de sempre, todas anteriores a esta linha de missões. Provas da
camada comercial: **95/95**.

Contratos: geografia **0 violações**, procedência **0 violações**, língua
**10 969 campos com IT+EN · 0 ainda só em português**.

---

## Resposta

```
SEMANTIC_RED_TEAM = PASS         (7 itens verificados, 0 falhas)
REGRESSAO_DO_RED_TEAM = PASS     (4 defeitos reproduzidos em 4b97cf5)
QA_PASS (ISTAT) = PARTIAL        2024 YES · 2025 YES · 2026 UNKNOWN

1 ER 5%           UNKNOWN — nunca NO sem medição que negue
2 VE carpocapsa   fase ENCERRADA + recomendação CONTINUAR + janela INDEFINIDA,
                  com donos separados. Fim do voo não é fim da necessidade.
3 FVG piralide    UNKNOWN — série fechada, nenhum registro inventado
4 TO botrite      cada elo com dono; a frase da janela prova UM elo
5 UM tignoletta   10–15% é da Umbria; direção fecha; WATCH
6 negativas       5 frases pinadas, incluindo o buraco de «fase conclusa»
7 reprocessamento 43 → 43 · 5 mudaram · 4 só na razão · nenhum estado subiu
8 regras ausentes 11 + 1 delegada; 1 coletada, pergunta escrita antes
9 ISTAT           testemunha verde, carimbo NÃO aplicado, custo medido
10 testes         T46–T58 · suíte 758/739 · 6 falhas e 2 erros pré-existentes

PORTAL      = NÃO TOCADO
DESIGN      = NÃO TOCADO
VERCEL      = NÃO TOCADO
PRODUÇÃO    = NÃO TOCADA
THRESHOLDS  = NÃO ALTERADOS
merge = NÃO   ·   publicação = NÃO
```
