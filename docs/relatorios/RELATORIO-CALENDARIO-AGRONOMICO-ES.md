# Calendário agronômico — quatro relógios, e nenhum empresta a semântica do outro

`2026-08-30` · engenharia de dado, contratos e views · **sem UI, sem pixel, sem cor**

---

## A pergunta que quebrou a coluna única

O portal precisa responder cinco coisas ao mesmo tempo:

- em que ponto do ciclo a cultura está;
- quando aquele problema costuma importar;
- se a janela registrada do produto ainda está aberta;
- que idade tem a evidência que sustenta a resposta;
- quando é preciso preparar o próximo ciclo.

São **quatro relógios diferentes** e a tentação era uma coluna chamada `WINDOW`. Ela teria feito o portal responder "janela aberta" para quem perguntou "há necessidade de tratar" — que é a confusão mais cara que este produto pode cometer, porque parece certa na tela.

    CROP_STAGE  !=  ISSUE_RELEVANCE_WINDOW  !=  REGISTERED_PRODUCT_WINDOW  !=  EVIDENCE_FRESHNESS

| relógio | pergunta | dono | por que **não** é um dos outros |
|---|---|---|---|
| A `crop_calendar` | onde a cultura está | tabela nova | não é janela de rótulo |
| B `issue_window` | quando o problema importa | tabela nova | **não guarda pressão atual** — pressão mora em `observacao` |
| C `registro_uso_janela` | até quando o rótulo autoriza | **filho** de `registro_uso` (006) | não é necessidade nem disponibilidade |
| D — sem tabela | que idade tem a evidência | função sobre `observacao` | depende de `as_of_date` e de propósito; persistir seria gravar um fato que muda sozinho |

O relógio C ser filho de `registro_uso` e o relógio D **não ter tabela** são as duas decisões de que mais me orgulho nesta rodada. Nenhuma delas cria um segundo dono.

## Precisão temporal virou coluna, com trava

`resolucao` é `DATE_EXACT / WEEK / MONTH / PHENOLOGY_STAGE / SEASON / APPROXIMATE / NOT_KNOWN`, e uma constraint confere que a resolução declarada bate com o campo preenchido. `MONTH` com `data_inicio` preenchida é **recusado pelo banco**, não corrigido por convenção.

Isso existe porque a conveniência de interface é o caminho mais curto para a invenção: um eixo de tempo precisa de um ponto, e "outubro/novembro" vira `2026-10-01` sem que ninguém decida. Aqui a interface muda; o dado não.

    "primavera"                 fica SEASON, não vira 2027-03-21
    "outubro/novembro"          fica MONTH, sem dia
    "BBCH 10-85"                fica PHENOLOGY_STAGE, e só se avalia contra fenologia observada
    "a partir de abril"         fica APPROXIMATE, com a frase literal junto

## UNKNOWN nunca é CLOSED

Uma janela em BBCH sem fenologia observada devolve `NOT_KNOWN`. Nunca `CLOSED`. A diferença é operacional: `CLOSED` diz "acabou", `NOT_KNOWN` diz "a fonte não me deu como decidir". O primeiro fecha uma conversa que deveria continuar.

E **não existe `CLOSING`**. Ele exigiria um limiar de N dias que ninguém acordou; inventar o estado seria inventar o limiar junto. Os estados são `ACTIVE / UPCOMING / CLOSED / OUTSIDE_MONTH_RANGE / OBSERVED / NOT_KNOWN / NO_DATA` e mais nenhum.

## O "hoje" não está gravado em lugar nenhum

Todo estado é derivado de `as_of_date` na hora da pergunta. Uma demo congelada em `2026-08-30` reproduz exatamente — hoje e daqui a um ano. A mesma linha do milho responde `ACTIVE` em `2026-06-20` e `CLOSED` em `2026-08-30`, e nada mudou no banco entre as duas perguntas.

## O que o motor descobriu, e que eu não tinha pedido

**1. `estado_frescor` estava colapsando duas ignorâncias.** Um propósito sem régua cadastrada recebia `STALE_FOR_PURPOSE` — isto é, o banco afirmava que a evidência era velha **sem ter limiar para medi-la**. Agora são três respostas distintas:

    sem data          -> AGE_NOT_KNOWN
    sem régua         -> NO_RULE_FOR_PURPOSE
    com data e régua  -> STALE_FOR_PURPOSE

**2. Um registro de nível cultura sumia da resposta.** O DIODE 100 é registrado para milho sem alvo nomeado. Ao perguntar pelo par milho × *Amaranthus palmeri*, ele desaparecia — e desaparecer é uma afirmação: "não há janela de produto". Agora ele vem, marcado `target_scope = CROP_LEVEL`.

**3. O NEPTUNE caducou quinze dias antes do `as_of_date`.** `fecha_caducidad = 2026-08-15`. O payload agora carrega `registration_state = "Vigente"` (a palavra do MAPA), `registration_expiry_date` e `registration_expiry_state = EXPIRY_DATE_PASSED` — os dois fatos lado a lado. **EXPIRY != WITHDRAWAL**: a data venceu; que o produto tenha sido retirado do mercado é outra afirmação, e este banco não a tem.

## A divergência que eu não vou maquiar

`ES-CASE-001` diz que a janela do NEPTUNE está **CLOSED**. O motor diz **NOT_KNOWN**.

O `CLOSED` do cartão é raciocínio humano somando *"se dará la primera aplicación antes de la floración"* com um prazo de segurança de 120 dias. A máquina se recusa a deduzir isso do dado guardado, porque `APPROXIMATE` não sustenta nem `ACTIVE` nem `CLOSED`.

**Os dois estão certos sobre coisas diferentes.** O humano concluiu; a máquina se recusou a concluir sem dado. Forçar acordo aqui seria ensinar o motor a inventar. O que resolveria de verdade: ler a data de floração do olival na fonte e guardá-la como fenologia observada — aí o motor teria como decidir. Fica **ABERTO**, registrado no contrato de handoff.

## O que foi executado, e onde

As migrations 010–012 **não foram aplicadas no Supabase** — isso continua sendo trabalho do workflow, com os segredos que só existem no GitHub Actions. Mas elas deixaram de ser proposta lida: rodaram num **PostgreSQL 16 local e descartável**, montadas do zero, na mesma ordem do workflow.

Foi essa execução que pegou o que a leitura estática não pegaria: a 011 referenciava `crop.nome_es`, coluna que a 009 tinha **removido** ao mover o vocabulário local para `crop_local` / `issue_local`. Um `psql` de dez segundos achou o que três leituras não acharam.

| prova | resultado |
|---|---|
| 001–007, 009–012 num banco vazio | 12 PASS |
| 008 (verificação) rodada por último | PASS · 30 tabelas, travas, funções e RLS |
| fixture ES | PASS |
| `regressoes_calendario.sql` | **45/45** |
| suíte Python | 459 testes, OK |

## As regressões foram testadas por mutação

Uma suíte verde que ficaria verde com o código errado não vale nada. Quebrei quatro leis de propósito, dentro de transações desfeitas, e conferi que a regressão correspondente reprova:

| mutação | regressão que pegou |
|---|---|
| janela imprecisa passa a fechar por data | 12 · UNKNOWN != CLOSED |
| a próxima janela passa a projetar campanha observada | 08 · FIRST_YEAR != RECURRING_CALENDAR |
| a idade da evidência passa a contar da data de captura | 04 · OBSERVATION_DATE != PUBLICATION_DATE |
| o isolamento de país cai | 18b · consulta FR devolve resposta ES |

E a 008 foi testada do mesmo jeito: removida a constraint `campanha_observada_nao_recorre`, ela reprova nomeando exatamente a trava que sumiu.

## Isolamento de país, medido e não afirmado

Toda função temporal exige `p_pais`. `f_paises_no_resultado_do_calendario('ES')` devolve `{ES}` nos três donos, e perguntar pela França num acervo só-ES devolve **vazio** — nunca a resposta da Espanha. Uma constraint recusa anexar geografia FR a um calendário ES: `SOURCE_LOCATION` pode ser outro país; `FACT_LOCATION` não.

## O que a fixture deliberadamente não tem

Ela carrega só dado com fonte. Está escrito no cabeçalho dela o que ficou de fora e por quê:

- **janela agronômica do repilo no outono** — a frase existe nos cartões, mas sem fonte citada. Seria calendário inventado.
- **qualquer data de 2027** nas tabelas de tempo — o caso do milho diz `NEXT_CYCLE`, e é só isso que a fonte sustenta. (A caducidade `2027-07-31` do ACCRESTO continua lá: é fato lido do registro espanhol, não calendário.)
- **pressão de campo dentro de `issue_window`** — pressão mora em `observacao`.

## Para o Claude Design

`AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1` diz o que o Design **recebe** e o que cada valor significa. Não diz como desenhar, e não carrega uma única cor — cor é do Design System.

O exemplo dentro dele **não foi escrito à mão**: é lido do banco por `scripts/calendario_handoff.py`. Se o motor mudar de resposta, o contrato muda junto ou o teste reprova. Contrato que descreve um payload que o código não produz é pior do que contrato nenhum.

`DISPLAY-LAYER-V1` ganhou **54 regras** em PT/EN/ES, cobrindo todo valor que o motor consegue emitir — e um teste confere essa cobertura enum por enum, porque uma enum nova sem regra de exibição chega crua na tela do cliente.

Duas proibições de tradução que valem em três línguas: nenhum estado desconhecido pode ser dito como fechado, e `EXPIRY_DATE_PASSED` nunca pode virar "retirado", "cancelado" ou "proibido".

## Duas honestidades pequenas

**O cabeçalho do `DISPLAY-LAYER-V1` não bate com o próprio arquivo.** `ACENTUACAO` diz que os textos de exibição levam acento; nenhuma das 29 regras anteriores leva. As 54 novas seguiram a convenção **real** do arquivo, para não deixá-lo meio acentuado. Corrigir os dois lados numa passada é trabalho do dono do DISPLAY-LAYER, não desta missão — está registrado dentro do próprio arquivo, em `DEFEITO_CONHECIDO_ACENTUACAO`.

**A marca `NÃO EXECUTADA` ficou imprecisa e foi corrigida** nas quatro migrations que esta missão tocou: elas não foram executadas *no Supabase*, mas foram executadas e conferidas num Postgres local. As migrations 001–007 e 009 mantêm a marca antiga, que o log do próprio workflow já contradiz — não é escopo desta rodada mexer nelas.

## O que esta missão não fez, de propósito

Não construiu HTML, não decidiu pixel, não redesenhou o portal, não inventou calendário e não coletou em massa. Não reabriu o Radar do Futuro nem o Display Layer — só os **estendeu** com a dimensão temporal. Não importou nada da branch local da ADAMA España: o contrato temporal está pronto para consumi-la quando o handoff daquela branch for validado, e nem uma linha foi adivinhada até lá.

---

## Arquivos

| arquivo | o que é |
|---|---|
| `supabase/migrations/010_calendario_agronomico.sql` | os quatro relógios: enums, tabelas, travas |
| `supabase/migrations/011_calendario_consultas.sql` | estado por data, por BBCH e por frescor; 4 views, 7 funções |
| `supabase/migrations/012_contexto_temporal_do_caso.sql` | o payload compacto do caso e a prova de isolamento |
| `supabase/migrations/008_verificacao_pos_aplicacao.sql` | estendida: confere os quatro relógios no banco real |
| `supabase/fixtures/es_calendario_mvp.sql` | Espanha, só dado com fonte |
| `supabase/tests/regressoes_calendario.sql` | 45 afirmações de significado contra Postgres real |
| `tests/test_calendario_temporal.py` | 37 regressões que não precisam de banco |
| `scripts/calendario_handoff.py` | monta o contrato do Design lendo o banco |
| `data/samples/AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1.json` | o que o Design recebe |
| `.github/workflows/calendario-regressoes.yml` | roda tudo isso num Postgres descartável, sem segredo |
