# SCRAP-OP-CLOSE — O PACOTE MÍNIMO DE DECISÃO DE VÍNCULO

> **A máquina está pronta. A conta existe. A fonte existe. O que não existe é a
> linha que diz que uma é a presença da outra.**
>
> ```
> SOURCE_ACCOUNT_BINDING     = NOT_PROVEN
> REAL_OPERATIONAL_COLLECTION = NOT_RUN
> FIRST_BREAK                = SOURCE_ACCOUNT_BINDING_HUMAN_DECISION
> ```
>
> Nenhuma coleta foi executada. Nenhuma decisão foi fabricada.

---

## 1 · O QUE SE PROCUROU, E ONDE

A pergunta era uma só: **existe uma conta real, explicitamente ligada a um
`SOURCE_ID` canônico, que uma capability `READY` consegue coletar de graça e
pontualmente pelo fluxo canônico?**

Procurou-se em todo o repositório por relações EXPLÍCITAS entre `SOURCE_ID`,
`PLATFORM` e conta. Seis ficheiros carregam os dois lados; três catálogos foram
lidos por inteiro; o atlas foi lido pelo scanner da própria casa.

---

## 2 · METADE DA CADEIA ESTÁ PROVADA, E ESTÁ BEM PROVADA

`data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json` liga **empresa × país ×
plataforma** a contas, com a evidência mais forte que existe nesta casa:

```
EVIDENCE_CLASS = PRIMARY_DECLARED_LINK
BY_IDENTITY_STATE = PROVED 32 · REJECTED 12 · NOT_KNOWN 28
ACCOUNTS_AUTHORIZED_FOR_COLLECTION = 22
```

E o critério não é semelhança de nome:

> «o site oficial local de BAYER em IT (`https://www.cropscience.bayer.it/`)
> declara este link. **Primeira parte falando de si própria — não é busca por
> nome.**»

Três perguntas independentes, e as três têm de fechar:

```
a conta é OFICIAL?  ·  é DAQUELE PAÍS?  ·  é da EMPRESA ou de uma MARCA?
```

Isto é exactamente o que a missão aceita como prova, e o oposto do que ela
recusa.

    PLAUSIBLE != PROVEN. E ESTA METADE ESTÁ PROVEN.

---

## 3 · A OUTRA METADE NÃO ESTÁ — E É A PRÓPRIA CASA QUE O DIZ

O catálogo liga contas a **empresas**. Ele não liga empresas a um `SOURCE_ID`
do atlas.

Medido no atlas, pelo scanner da casa:

```
FONTES DO ATLAS                                   23
FONTES DO ATLAS COM URL DE CONTA DE PLATAFORMA     0
```

E o único candidato a fazer essa ponte está registado como **decisão pendente**,
por escrito, por uma missão anterior:

```
candidatas/ITALY-SOURCE-MASTER-V1.json
  SOURCE_ID  IT-T9-001
  STATUS     REDEFINED
  redefinition_note:
    «IT-T9-001 existia como ficha COMPARTILHADA FR/ES/IT que não media empresa
     a empresa. A missão exige medir cada uma. Proposta: manter o ID e abrir
     IT-T9-002..008 por empresa. REQUER DECISÃO — o ID já está contado no
     placar do Atlas.»

  duplication_analysis/PRE_EXISTING_NEEDS_DECISION[0] = IT-T9-001
```

A ficha do atlas nomeia as empresas — *«páginas de atualidades de BASF, Bayer,
Syngenta, Corteva…»* — e ao mesmo tempo declara que **não mede empresa a
empresa**. As duas frases são verdadeiras, e juntas não fecham um vínculo.

    UMA FICHA QUE NOMEIA A EMPRESA E DIZ QUE NÃO A MEDE
    NÃO É UM VÍNCULO COM A CONTA DELA.

Escolher sozinho aqui seria exactamente a inferência que a missão proíbe: a
conta é da BASF, a ficha fala da BASF, logo a conta é da ficha. É plausível, e
plausível não é provado.

---

## 4 · OS TRÊS CANDIDATOS

Todos na mesma plataforma `READY`, todos `PROVED + LOCAL_COUNTRY_PROVED +
PAGE_ROLE=COMPANY + COLLECTION_AUTHORIZED=YES`, todos da linha italiana.

### CANDIDATO 1 — Bayer Italia

```
PLATFORM                    INSTAGRAM   (instagram.profile.discovery · READY · grátis)
ACCOUNT                     bayer_italia
ACCOUNT_URL                 https://www.instagram.com/bayer_italia/
POSSIBLE_SOURCE_ID          IT-T9-001
EVIDENCE_FOR_LINK           o site oficial de Bayer em IT (cropscience.bayer.it,
                            título «Bayer Crop Science Italia») declara esta conta,
                            em primeira parte. A ficha IT-T9-001 nomeia a Bayer.
EVIDENCE_AGAINST            a ficha é COMPARTILHADA FR/ES/IT e declara que «não
                            mede empresa a empresa»; a proposta em aberto é
                            reatribuir IT-T9-001 à BASF, não à Bayer.
CONFIDENCE_NOT_USED_AS_PROOF  alta plausibilidade, e ela não conta
WHAT_HUMAN_MUST_DECIDE      se esta conta é presença oficial de IT-T9-001
```

### CANDIDATO 2 — Syngenta Italia

```
PLATFORM                    INSTAGRAM   (instagram.profile.discovery · READY · grátis)
ACCOUNT                     syngentaitalia
ACCOUNT_URL                 https://www.instagram.com/syngentaitalia/
POSSIBLE_SOURCE_ID          IT-T9-001
EVIDENCE_FOR_LINK           o site oficial de Syngenta em IT (syngenta.it, título
                            «Syngenta Italia | Soluzioni innovative per
                            l'agricoltura») declara esta conta, em primeira parte.
                            A ficha IT-T9-001 nomeia a Syngenta.
EVIDENCE_AGAINST            a mesma: ficha compartilhada, e a proposta em aberto
                            aponta IT-T9-001 para a BASF.
CONFIDENCE_NOT_USED_AS_PROOF  alta plausibilidade, e ela não conta
WHAT_HUMAN_MUST_DECIDE      se esta conta é presença oficial de IT-T9-001
```

### CANDIDATO 3 — BASF Italia

```
PLATFORM                    INSTAGRAM   (instagram.profile.discovery · READY · grátis)
ACCOUNT                     basf_global
ACCOUNT_URL                 https://www.instagram.com/basf_global/
POSSIBLE_SOURCE_ID          IT-T9-001
EVIDENCE_FOR_LINK           é a empresa que a proposta em aberto nomeia para
                            IT-T9-001, com a URL da ficha (agro.basf.it) a bater
                            com o site que declara a conta.
EVIDENCE_AGAINST            a conta declarada é GLOBAL, não italiana, e por isso o
                            próprio catálogo a marca COLLECTION_AUTHORIZED = NO.
                            Coletá-la seria coletar o grupo, não a Itália.
CONFIDENCE_NOT_USED_AS_PROOF  é o candidato com melhor razão documental e a pior
                            prova de país — e as duas coisas são verdade ao mesmo tempo
WHAT_HUMAN_MUST_DECIDE      se esta conta é presença oficial de IT-T9-001
```

---

## 5 · A PERGUNTA, E SÓ ELA

Para cada candidato, uma pergunta. Nada mais.

> **Esta conta é uma presença oficial da fonte `IT-T9-001`?**
>
> `SIM` / `NÃO` / `NÃO SEI`

Um `SIM` a qualquer um deles destrava uma coleta real mínima, gratuita e
pontual, pelo fluxo canônico, sem tocar a porta paga.

Um `NÃO SEI` é uma resposta legítima e fica registada como tal — foi por não
haver nenhuma que esta missão parou.

---

## 6 · O QUE NÃO SE FEZ, E POR QUÊ

- **Não se executou coleta.** Sem vínculo provado, a corrida ou entregaria zero
  por lei, ou carimbaria um `SOURCE_ID` que ninguém ligou àquela conta.
- **Não se escreveu no livro de relevância.** Medido: para rota gratuita e
  pontual o contrato **não** a exige, então não havia o que decidir ali.
- **Não se avaliaram as 77 fontes.** Três candidatos, uma pergunta.
- **Não se criou `SOURCE_ID` novo.** Abrir `IT-T9-002..008` é a mesma decisão
  humana, vista do outro lado, e o master já regista o bloqueador: o ID actual
  já está contado no placar do atlas.
- **Não se tocou em Meta, X, Facebook, Threads, nem na arquitetura.**

---

## 7 · O QUE A PRÓXIMA MISSÃO ENCONTRA PRONTO

Se a resposta vier `SIM`, o caminho já está inteiro e provado:

```
REQUEST -> RECIPE -> ORCHESTRATOR -> SCRAP -> ROUTER -> ADAPTER
        -> NETWORK -> RAW -> RETURN CONTRACT -> COLLECTION BOUNDARY
```

E um aviso medido, para não surpreender ninguém: `instagram.profile.discovery`
está `READY` e corre em `LOCAL` com `DATACENTER_BLOCKED`. Ela precisa do runner
com navegador, e não deste ambiente.

    READY NÃO É «CORRE EM QUALQUER MÁQUINA».
    É «A ENGENHARIA ESTÁ COMPLETA E O PORTÃO DEIXA PASSAR».
