# MAPA DE IDENTIDADE E ONTOLOGIA AGRÍCOLA — V1

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    PROPOSTA DE DIRECCAO — NAO IMPLEMENTA NADA
MEDIDO_EM  2026-09-13
```

> **Nada aqui é implementado.** Zero runtime, zero migration, zero tabela, zero
> alteração de contrato de fonte, zero Admission, zero Bíblia, zero System Map.
> Isto responde *como devemos identificar*, não *como vamos persistir*.

---

## 0 · A LEI QUE JÁ EXISTE, E QUE ESTE MAPA NÃO REESCREVE

A `COL-LAW-203` já diz o que o §10 do enunciado propõe como lei candidata:

> **«NORMALIZAÇÃO NÃO DESTRÓI O VALOR ORIGINAL.»**
> *«qual fonte disse · qual artefato disse · qual era o valor original · qual
> valor normalizado saiu · quando o SINTONIA viu · qual regra produziu a
> normalização»*

```
A LEI CANDIDATA DO §10 JA E LEI DESTA CASA.
O QUE FALTA NAO E A LEI. E O SITIO ONDE ELA SOBREVIVE ATE A INTELLIGENCE.
```

O benchmark externo confirma-a de três lados independentes: a EPPO mantém o
código quando o nome muda (o original e o canónico não são o mesmo objecto);
a AGROVOC guarda `prefLabel` por língua sobre uma URI estável; a Crop Ontology
cria **variável nova** quando o método muda em vez de sobrescrever a antiga.

E acrescenta **um quarto elemento que a `COL-LAW-203` não nomeia**: a
*versão da autoridade normalizadora*. Ver §4.

---

## 1 · A TABELA — CONCEITO A CONCEITO

Legenda de `LIMIT`: o que este identificador **não** resolve.

### CROP

```
PREFERRED_EXTERNAL_ID   EPPO code (5 letras) — VITVI, TRZAX, PRNAV
LOCAL_ID_IF_NEEDED      nao e preciso: o EPPO cobre cultivada e silvestre
ORIGINAL_TERM_PRESERVED SIM, obrigatorio — «Vigne», «frumento tenero», «Vite»
NORMALIZED_TERM         nome cientifico preferido da EPPO
SYNONYMS                nomes comuns EPPO por lingua + AGROVOC prefLabel/altLabel
VERSIONING              codigo estavel; NOME muda -> guardar a data da leitura
LIMIT                   40 de 105 pares resolvidos nesta casa tem EPPO_CROP e
                        CANONICAL_CROP = null: o codigo existe ao nivel de
                        genero/agregado (TRZAX = Triticum), nao de especie.
                        «Cereali a paglia» nao e uma especie e nao deve receber
                        codigo de especie — RECUSAR e o comportamento certo.
```

### CROP GROUP

```
PREFERRED_EXTERNAL_ID   EPPO non-taxonomic code — comeca por «3», termina em «C»
                        (ex. 3CITC = citrus fruit crops)
ORIGINAL_TERM_PRESERVED SIM
LIMIT                   GRUPO NAO E ESPECIE. Um uso de rotulo autorizado para
                        um GRUPO nao autoriza cada especie do grupo por
                        deducao nossa — quem decide e o rotulo.
```

### PEST · DISEASE · PATHOGEN · WEED

```
PREFERRED_EXTERNAL_ID   EPPO code (6 letras) — PLASVI, PUCCRT, PUCCST
ORIGINAL_TERM_PRESERVED SIM, obrigatorio — «Mildiou(s)», «Peronospora»,
                        «Rouille(s)», «Moniliose(s) et pourriture grise»
NORMALIZED_TERM         nome cientifico preferido EPPO
SYNONYMS                nomes comuns EPPO por lingua (a ponte que funciona)
VERSIONING              codigo estavel sob mudanca taxonomica
LIMIT                   A RELACAO E 1:N. Medido: «Rouille(s)» em Ble -> PUCCRT
                        **e** PUCCST. «Moniliose(s) et pourriture grise» em
                        Cerisier -> GLOMCI **e** PHYTCC. Forcar 1:1 mente.
                        E DISEASE != PATHOGEN: a EPPO codifica o organismo;
                        o nome da doenca vive nos nomes comuns, nao no codigo.
```

### TARGET (o alvo de um uso de PPP)

```
PREFERRED_EXTERNAL_ID   EPPO non-taxonomic «3…T» quando o alvo e um grupo ou
                        um efeito (regulador de crescimento); EPPO taxonomico
                        quando e organismo
LIMIT                   TARGET != PEST. O alvo do rotulo pode ser um grupo, um
                        efeito ou um estado — e nao tem de ser um organismo.
```

### ACTIVE SUBSTANCE

```
PREFERRED_EXTERNAL_ID   nome ISO da substancia activa + **CAS** quando existir
SECUNDARIO              identificador da EU Pesticides Database
ORIGINAL_TERM_PRESERVED SIM — a grafia nacional muda («metiram», «metiran»)
VERSIONING              o ESTADO de aprovacao UE tem data e regulamento; o
                        estado NAO e propriedade da substancia, e um facto
                        datado sobre ela
LIMIT                   CAS identifica a molecula, nao a aprovacao, nao o teor,
                        nao a formulacao. Variantes (sais, esteres) sao
                        moleculas diferentes com CAS diferentes.
```

### PRODUCT (produto comercial)

```
PREFERRED_EXTERNAL_ID   NAO EXISTE identificador internacional
LOCAL_ID_IF_NEEDED      SIM — e obrigatorio: chave (pais, registration_id)
ORIGINAL_TERM_PRESERVED SIM — o nome comercial e o que o agricultor conhece
VERSIONING              a composicao e o rotulo mudam DENTRO do mesmo numero
LIMIT                   O MESMO NOME COMERCIAL E PRODUTOS DIFERENTES EM PAISES
                        DIFERENTES. Nome comercial NAO e identidade.
                        A COL-LAW-034 ja o diz: «BRAND nao e a oitava entidade:
                        e o PAPEL de duas delas.»
```

### REGISTRATION

```
PREFERRED_EXTERNAL_ID   (pais, numero de registo) — em Italia, o numero
                        atribuido pelo Ministero della Salute
ACOMPANHA               data do decreto, data de caducidade, stato
                        amministrativo (autorizzato · revocato · scaduto ·
                        sospeso)
VERSIONING              obrigatorio: o registo tem historia, e a historia e o
                        objecto de Future/Regulatory Intelligence
LIMIT                   registro-na-base != ato-oficial. Guardar o ato.
```

### LABEL (etichetta / rótulo)

```
PREFERRED_EXTERNAL_ID   NAO EXISTE — identifica-se por (registration_id, versao)
OBRIGATORIO             o DOCUMENTO, com sha256 e data
VERSIONING              a versao do rotulo E o objecto; a base da a «ultima
                        etichetta autorizzata», e a anterior desaparece da
                        vista — se nao a guardarmos, perdemo-la
LIMIT                   ROTULO != AUTORIZACAO. O rotulo e o texto do ato; o
                        ato e o decreto.
```

### PPP USE — **a unidade que faltava**

```
PREFERRED_EXTERNAL_ID   EPPO PP 1/248 (3) — combinacao de SEIS elementos,
                        cada um com o seu codigo EPPO:
                          CROP / CROP GROUP      (3…C)
                          TREATED OBJECT         (3…O)
                          TARGET                 (3…T)
                          CROP DESTINATION       (3…D)
                          LOCATION OF USE        (3…L)
                          TREATMENT              (3…M)
ACOMPANHA               dose, numero de aplicacoes, intervalo, estadio (BBCH),
                        PHI/intervallo di sicurezza, restricoes
LIMIT                   NAO E UM PAR (produto, cultura). Um sistema que guarde
                        so o par perde destino, local, objecto e tratamento —
                        e e com esses que se decide se um uso serve.
```

### COMPANY / HOLDER

```
PREFERRED_EXTERNAL_ID   NAO EXISTE global. Candidatos: LEI, VAT nacional
LOCAL_ID_IF_NEEDED      SIM
LIMIT                   A COL-LAW-034 ja separa SETE entidades no regulatorio
                        (REGISTRATION_ID · REFERENCE_PRODUCT · REFERENCE_HOLDER
                        · MANUFACTURER · MANUFACTURING_SITE ·
                        COMMON_DENOMINATION · CONCESSIONAIRE) e ja tem a
                        cicatriz medida: «linkedin.com/company/adama/» devolve
                        uma incorporadora imobiliaria romena.
                        IDENTIDADE NUNCA POR SIMILARIDADE TEXTUAL.
```

### GEOGRAPHY · FIELD / AREA / REGION

```
PREFERRED_EXTERNAL_ID   NUTS (NUTS0..NUTS3) para area administrativa europeia
                        + codigo ISTAT do comune em Italia
COORDENADA              GeoJSON, com CRS declarado
FIELD                   field boundary — poligono. NAO TEMOS, e nao vamos ter
                        sem dado privado
ORIGINAL_TERM_PRESERVED SIM — «Provincia di Verona», «Veneto»
LIMIT                   NUTS MUDA DE VERSAO (NUTS 2016/2021/2024) e as
                        fronteiras mudam com ela: a versao NUTS faz parte da
                        identidade do lugar. E a escada epidemiologica da EFSA
                        (populacao-alvo -> unidade epidemiologica -> unidade de
                        inspecao) NAO e traduzivel para NUTS.
```

### PHENOLOGICAL STAGE

```
PREFERRED_EXTERNAL_ID   BBCH (codigo decimal 00–99), com a escala da especie
ORIGINAL_TERM_PRESERVED SIM — «fioritura», «floraison», «floracao»
LIMIT                   BBCH OBSERVADO != BBCH MODELADO. Uma escala nao diz
                        quem a leu. E BBCH descreve a PLANTA, nao a doenca:
                        nao substitui janela de infeccao.
```

### OBSERVATION VARIABLE · METHOD · UNIT · SCALE

```
PREFERRED_EXTERNAL_ID   Crop Ontology Variable ID (CO_xxx:…) quando existir
ESTRUTURA               VARIAVEL = TRAIT x METHOD x SCALE  (lei externa)
UNIT                    unidade explicita, sempre; converter e uma operacao
                        com registo (o Agmatix tem um motor so para isso)
DENOMINADOR             quando a medida e uma proporcao, o denominador NAO e
                        opcional — «12,5 %» sem «de 100 folhas» nao e um numero
LIMIT                   A Crop Ontology e de MELHORAMENTO e agronomia
                        experimental. Nao tem variavel para «pressao de doenca
                        relatada num boletim regional». Onde nao houver
                        variavel canonica, guardar TRAIT+METHOD+SCALE em texto
                        preservado e marcar NAO_NORMALIZADO — nunca inventar
                        um CO_ id.
```

### SCIENTIFIC STUDY

```
PREFERRED_EXTERNAL_ID   DOI
AUTOR                   ORCID quando existir
ENSAIO                  MIAPPE investigation/study ID; BrAPI trialDbId
LIMIT                   DOI IDENTIFICA A PUBLICACAO, NAO O ENSAIO.
                        Tres DOIs podem ser um ensaio. Um DOI pode conter
                        varios ensaios. A COL-LAW-218 ja diz que preprint,
                        versao publicada e versao corrigida podem ser o mesmo
                        trabalho canonico sem serem o mesmo artefato.
```

### PEST RECORD / PEST STATUS (ISPM 8)

```
PREFERRED_EXTERNAL_ID   NAO EXISTE id publico por registo
ESTRUTURA               (praga, hospedeiro, AREA, data, fonte) -> registo
                        (praga, AREA, data) -> ESTADO, com qualificador
LIMIT                   O ESTADO E UMA CONCLUSAO DE UMA AUTORIDADE, NAO UMA
                        SOMA DE REGISTOS. E ele anda para tras:
                        «pest records invalid» · «pest no longer present».
```

---

## 2 · QUANDO CADA IDENTIFICADOR PODE SER USADO

| id | pode ser usado para | **não** pode ser usado para |
|---|---|---|
| `EPPO CODE` | organismo, cultura, grupo, alvo, objecto tratado, destino, local, tratamento | nome de doença; medição; fase; produto |
| `CAS` | molécula | aprovação; formulação; teor |
| `registration number` | produto num país | produto noutro país; carteira comercial |
| `DOI` | publicação | ensaio; resultado; independência |
| `ORCID` | pessoa autora | perícia no assunto (`INT-LAW-065`) |
| `NUTS` | área administrativa, **com versão** | talhão; população epidemiológica |
| `BBCH` | fase da planta | janela de infecção; risco |
| `AGROVOC URI` | conceito e as suas línguas | identidade taxonómica; medição |
| `Crop Ontology ID` | variável observada | organismo; produto |
| `PP1/248 tuple` | **uso** de PPP | produto; autorização |

```
NAO HA UM VOCABULARIO UNIVERSAL, E ESCOLHER UM SO POR CONVENIENCIA
SERIA ESCOLHER QUAL DAS PERGUNTAS DEIXAR DE PODER FAZER.
```

---

## 3 · A FORMA CANDIDATA DE UM VALOR NORMALIZADO

Derivada da `COL-LAW-203` e do que a EPPO/Crop Ontology/AGROVOC obrigam. **Não é
uma tabela; é o conjunto mínimo que tem de sobreviver:**

```
ORIGINAL_VALUE            "Mildiou(s)"
ORIGINAL_LANGUAGE         FR
ORIGINAL_CONTEXT          o par do rotulo: (cultura = "Vigne")
NORMALIZED_ID             PLASVI
NORMALIZED_TERM           Plasmopara viticola
NORMALIZATION_AUTHORITY   EPPO Global Database
AUTHORITY_READ_AT         2026-08-28
AUTHORITY_VERSION         NAO SEI          <- o buraco, ver §4
NORMALIZATION_RULE        motor/normalize_agro.py :: verify
RULE_VERSION              NAO SEI          <- o segundo buraco
MATCH_TYPE                CONTEXTUAL
MATCH_EVIDENCE            «EPPO GD PLASVI: nome frances "mildiou de la vigne"»
CARDINALITY               1  (ou N, e entao NORMALIZED_ID e uma lista)
```

E o exemplo que prova que a cardinalidade não é decorativa:

```
ORIGINAL_VALUE   "Rouille(s)"  em  ORIGINAL_CONTEXT  (cultura = "Ble")
NORMALIZED_ID    [PUCCRT, PUCCST]
MATCH_TYPE       GROUP_SCOPED
MATCH_EVIDENCE   «grupo delimitado pela cultura — EPPO GD confirma para Ble»
```

---

## 4 · OS DOIS BURACOS DA NORMALIZAÇÃO, MEDIDOS

O dicionário agro canónico desta casa
(`data/samples/X-007-canonical-agro-dictionary.json`) preserva **o original, o
normalizado, a evidência e o tipo de correspondência**. Isso é mais do que a
maioria dos sistemas faz, e está certo.

O que ele **não** preserva:

```
1. AUTHORITY_VERSION
   Guarda `captured_at: 2026-08-28`. Nao guarda que versao da EPPO Global
   Database respondeu. Quando a EPPO reclassificar — e vai —, nao ha como
   saber se a nossa leitura e de antes ou de depois.

2. RULE_VERSION
   Guarda o ficheiro que normalizou. Nao guarda a versao da regra.
   A COL-LAW-042 ja escreveu porque isto importa:
   «A VERSAO DA REGRA E O QUE PERMITE REPROCESSAR.»
   Sem ela, «reprocessa tudo o que a regra v1 resolveu como AMBIGUOUS» nao e
   uma operacao: e refazer tudo.
```

E o terceiro, que é de arquitetura e não de campo:

```
3. O DICIONARIO E UM FICHEIRO, NAO UMA CAMADA.
   `motor/normalize_agro.py` importa `coleta/eppo_gd.py`, que faz HTTP ao vivo
   a `gd.eppo.int`. O censo da Intelligence ja mediu isto e classificou-o:
   `SEVERITY = ARCHITECTURAL` — INTELLIGENCE -> COLETOR DIRECTO, sem passar
   por COLLECTION -> SALA DE ESPERA -> INTELLIGENCE.
   E mediu tambem que ninguem anda esse caminho:
       DIRECT_COLLECTION_PATHS = 1 (existe em codigo)
       EXERCIDOS POR ALGUMA ROTA = 0 (CAN DO != DID DO)
```

---

## 5 · ONDE A NORMALIZAÇÃO PERTENCE — E ONDE NÃO PERTENCE

```
COLLECTION   guarda o ORIGINAL, e guarda-o sempre.
             Guarda o NORMALIZADO **quando a fonte ja o traz**
             (o registo espanhol traz EPPO; o frances nao).

INTELLIGENCE normaliza o que a fonte nao normalizou, e escreve como o fez.
             `INT-LAW-083`: entity resolution NAO fabrica identidade da
             Collection. `INT-LAW-084`: conflito de normalizacao permanece
             conflito.

NENHUM DOS DOIS apaga o original. `COL-LAW-203`.
```

E o portão que falta, dito na linguagem do enunciado:

```
ORIGINAL SEM NORMALIZADO   = incompleto, e util
NORMALIZADO SEM ORIGINAL   = irreversivel, e por isso PROIBIDO
NORMALIZADO SEM AUTORIDADE E VERSAO = irreproduzivel
```

---

## 6 · VEREDITO

```
ONTOLOGY_DIRECTION_READY = YES
```

A direcção está pronta porque as perguntas têm dono externo comprovado e os
limites estão medidos, não supostos: EPPO para organismo e uso, Crop
Ontology/MIAPPE para medição, BBCH para fase, NUTS (com versão) para área
administrativa, DOI/ORCID para ciência, ISPM 8 para estado de praga, e
identificador local **obrigatório** para produto e registo — porque aí não
existe identificador internacional e fingir que existe seria o erro.

O que **não** está pronto é a persistência, e ela não é decidida aqui.
