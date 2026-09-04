# O CONTRATO DE FONTE DO BRASIL — e o que a Itália tem de fazer para caber nele

**Data:** 2026-09-04 · **Missão:** UPSTREAM · **PR:** não aberto

**Itália:** `eame-sintonia` · branch `claude/human-agricultural-sensors-8fv0fw` · HEAD `35f79c8`
**Brasil:** `lucianodalondon-sys/portal-sintonia` · HEAD `38e4b8d` · clone `/home/user/portal-sintonia`

> ⚠️ **Aviso de método, e ele invalida a régua que eu ia usar.** O repositório brasileiro
> tem **um único commit** (`38e4b8d`, 2026-08-27). `git log -1 --format=%ci` devolve a
> mesma data para os 133 documentos e os ~100 scripts, e **não separa vivo de legado**.
> A recência foi decidida por três sinais: execução em `.github/workflows/*.yml`,
> importação por arquivo vivo, e as datas que a própria casa escreve dentro do código.

---

## 1 · A ARQUITETURA QUE O BRASIL TEM — e ela responde a pergunta da Itália

O Brasil **já separa** ORIGEM de PAPEL de CANAL. A Itália não precisava inventar nada.

```
public.entidades      QUEM É        chave(unique) · nome_canonico · tipo · entidade_mae
                                    · uf · cidade · origem_local · evidencia
                      tipo ∈ pessoa · empresa · cooperativa · veiculo · orgao

public.fontes         ONDE EU BATO  entidade_id → entidades · papel_da_fonte
                                    · external_id · plataforma · handle · canal_youtube
                                    · url · canonical_url · tipo · culturas · pracas
                                    · alcance · cadencia_dias · ultima_coleta   (63 colunas)
                      papel_da_fonte ∈ company · person · marca · canal_tecnico · veiculo

public.enderecos      OS N ENDEREÇOS DE UMA FONTE, com como_achou · evidencia · confianca

public.documentos     fonte_id      ⛔ documento NUNCA aponta para entidade
```

**A lei, escrita no comentário da própria tabela** (`entidades.sql:78-93`):

> *"QUEM É — pessoa, empresa, cooperativa, veiculo, orgao. Uma entidade tem N fontes
> (contas/canais), inclusive várias da MESMA plataforma: o Canal Rural tem dois canais de
> YouTube e um site. Documento NUNCA aponta para cá."*
>
> *"**LIGAR, nunca fundir**: as linhas de fontes continuam separadas, e quem soma por
> entidade é a camada de análise (escopo declarado: fonte · plataforma · entidade)."*

E o custo de fundir foi **medido antes de acontecer** (`PLANO-entidade-e-fonte.md`): dos 55
grupos que um programa chamava de "PODE FUNDIR", **39 eram a mesma pessoa em plataformas
diferentes**, com **8.687 documentos**. Fundir teria apagado *qual plataforma disse o quê*.

---

## 2 · ⚠️ O CONTRATO ESTÁ ESCRITO, MAS NÃO ESTÁ OPERANTE

Esta é a correção mais importante desta rodada, e ela corrige **o que eu mesmo disse antes
de medir**. Eu li `PLANO-location-resolver.md:683` — *"✅ `fontes.entidade_id` — 3.275 de
3.299 · medido"* — e relatei que a separação estava viva. **O inventário do banco real diz
outra coisa:**

```
fontes 4.517 · enderecos 3.627 · v_pessoa_e_canais 4.494 · entidades 57 · pessoas 50
```

| peça | estado real |
|---|---|
| `public.entidades` | **57 linhas para 4.517 fichas — 1,3%** |
| `public.pessoas` | 50 linhas |
| `public.enderecos` | 3.627 linhas e **nenhum leitor operacional** — classificada `FIO CORTADO` em 18/08 |
| `v_pessoa_e_canais` | 4.494 linhas, **nunca aberta por programa nenhum** |
| `fontes.papel_da_fonte` | **zero linhas gravadas** — o campo que responderia a pergunta italiana de PAPEL é o único completamente vazio |

E a cobertura de `entidade_id` tem **divergência grave e não resolvida dentro do próprio
repositório**: `MAPA-DOS-DADOS.md:180` (12/08) diz *47 entidades, 95 fichas ligadas*; o
inventário de 19/08 e o relatório de 23/08 dizem *57*; `PLANO-location-resolver.md:683`
diz *3.275 de 3.299*. Três números, o mesmo período.

> **O sistema vivo continua rodando com UMA linha de `public.fontes` fazendo papel de
> origem e canal ao mesmo tempo.** A Itália não deve copiar o estado; deve copiar o
> **contrato** — que é bom — e chegar nele com dado, que é o que o Brasil ainda não fez.

A razão de `papel_da_fonte` estar vazio está escrita, e é uma boa razão:
*"Encher a coluna para completar esquema criaria uma SEGUNDA VERDADE só para compará-la
com a primeira — o oposto de auditar."*

---

## 3 · O VOCABULÁRIO CANÔNICO — 20 valores, e a armadilha da lista obsoleta

`fontes.tipo`, CHECK vigente em **`tipos-de-fonte.sql:38-66`**:

```
creator · imprensa · portal · cooperativa · associacao · instituicao · podcast
revenda · distribuidor · congresso · orgao_publico
pesquisador · tecnico · comercial · operador · produtor · estudante          ← gente
comite_tecnico · laboratorio · empresa                                        ← organização
```

> ⚠️ **Existe uma restrição ANTIGA de 11 valores em `supabase-conteudo.sql:12-16`, e ela é
> a PRIMEIRA que aparece quando se procura `check (tipo in (...))`.** A própria casa
> avisa em `onde-esta-o-tecnico.py:417-424` que quem procurar sem âncora pega a lista
> obsoleta. Eu quase peguei.

**As cinco famílias humanas** — o cânon analítico, `vozes-do-acervo.py:128-140`:

| família | tipos que caem nela |
|---|---|
| **A · CIÊNCIA** | pesquisador · instituicao · laboratorio · comite_tecnico |
| **B · AGRÔNOMO** | tecnico |
| **C · RTV** | comercial |
| **D · CAMPO** | produtor |
| **E · MERCADO** | cooperativa · revenda · distribuidor · empresa |

E o que não foi nomeado **não é enfiado numa das cinco**: sai em `FORA_DAS_CINCO`, visível.
Só 11 dos 20 tipos estão mapeados, e isso é deliberado.

**Agrupamento de leitura** (`camadas-do-campo.py:81,84`):
`DO_CAMPO = tecnico · pesquisador · produtor · cooperativa` ·
`INSTITUCIONAL = instituicao · associacao` — e `instituicao` **saiu** de DO_CAMPO por medição.

---

## 4 · ⛔ DEFEITOS BRASILEIROS QUE A ITÁLIA **NÃO** DEVE PROPAGAR

O usuário mandou verificar se continuam verdadeiros. Continuam — e são medidos.

| # | defeito | medida | Itália deve |
|---|---|---|---|
| D1 | **`creator` é a gaveta padrão, não um papel** | **2.491 de 4.543 fichas (54,8%)** estão em `creator` | ⛔ **não copiar.** A Itália usa `creator` **zero** vezes — e isso é uma vantagem acidental que deve virar regra escrita |
| D2 | **`tipo` é valor ÚNICO, sem array — papel verdadeiro se perde** | *"Engenheiro Agrônomo \| Pesquisador"* vira `pesquisador`, e o agrônomo some | ⛔ **corrigir.** É exatamente a trava do usuário: *"pessoa não deve perder um papel verdadeiro porque outro recebeu peso maior"* |
| D3 | **`agronomo` e `consultor` NÃO existem** como valores | dobrados dentro de `tecnico` (`tipos-de-fonte.sql:59`) | ⚠️ herdar com perda **declarada** — a Itália distingue os dois e a tradução funde |
| D4 | **Quatro taxonomias paralelas que discordam** | `CENSO-DA-IDENTIDADE-ANALITICA.md:277`: *"`camada-da-fonte.sql` ⚠️ taxonomia PARALELA — ⛔ NÃO criar uma terceira"* | ⛔ a Itália criou **uma quarta**. Este documento é o começo de desfazê-la |
| D5 | **`camada` foi DERIVADA de `tipo` por UPDATE** | `camada-da-fonte.sql:110-125` | ⛔ não tratar como segunda testemunha — é a mesma testemunha duas vezes |
| D6 | **`cooperativa` mora em três lugares que discordam** | `vozes-do-acervo` → E·MERCADO; `camadas-do-campo` → DO_CAMPO; `camada-da-fonte.sql` → tecnico | ⛔ escolher um e declarar |
| D7 | **Dois terços do "técnico" não é técnico** | dos 64.612 documentos rotulados técnico pelo FORMATO, só 31,9% vêm de canal `tecnico`; 24,4% são pesquisador, 23,6% creator | ⚠️ nunca inferir papel a partir do formato do documento |
| D8 | **Google Scholar colapsa em `external_id` único** | `url_canonica('…/citations?user=gQFhY0UAAAAJ')` → `scholar.google.com/citations` — o id do autor **sai inteiro** | ⛔ **defeito NÃO registrado na casa brasileira**, achado nesta auditoria. A Itália não deve herdar a normalização que corta query-string para identificadores que vivem nela |
| D9 | **Duas listas vivas de CULTURA** | `vocabulario.py` CULTURA=9 (em produção) vs `lavouras.py` CULTURAS=23 (autodeclarado dono único); 9 em comum e **as 9 divergem em padrão** | ⛔ a Itália deve escolher **um** dono antes de mapear cultura |

---

## 4-B · OS CINCO ANTÍDOTOS BRASILEIROS QUE A ITÁLIA PODE COPIAR HOJE

A auditoria brasileira catalogou **24 defeitos de classificação de fonte**, todos com
`arquivo:linha`. O eixo que organiza quase todos é um só:

> ## ⛔ A CASA CLASSIFICA PELO CONTINENTE E CHAMA DE CONTEÚDO.

`fontes.tipo` **não é classificação — é o valor padrão que o `NOT NULL` obrigou.** 54,8% do
cadastro é `creator`, **14 arquivos o gravam fixo** (inclusive o que caça técnicos), e a
conclusão da auditoria é literal:

> *"Segmentar captação por PAPEL hoje é segmentar pelo DEFAULT de quem cadastrou."*

Cinco antídotos são copiáveis **sem criar taxonomia nova**:

| # | antídoto | o que resolve |
|---|---|---|
| **A1** | **As QUATRO respostas ao vazio, e nenhuma vira a outra:** `FALTA` · `NAO_SE_APLICA` · `NÃO SEI` · *"perguntamos e ela não tem"* | a Itália hoje tem **uma** (`NÃO SEI`), e por isso não distingue *"não perguntei"* de *"não existe"* |
| **A2** | **Decompor em DOIS PASSOS:** o formato do documento responde bem *dono × plateia*, e **nunca** responde *pesquisador × agrônomo × RTV × produtor* | impede inferir papel a partir do formato |
| **A3** | **"Citar uma instituição não te transforma nela":** sigla de organização só conta **no nome**; no corpo do texto é **vínculo**, e vínculo tem campo próprio | é exatamente o defeito **I4** italiano (Medical Excellence TV → `RESEARCH_ORGANIZATION`) |
| **A4** | **Assimetria de custo declarada num arquivo único com três estados** — descartar quem É do agro custa muito mais que aceitar quem não é | a Itália rejeitou 4.525 candidatos sem nunca ter declarado essa assimetria |
| **A5** | **Promover só quem está no balde, nunca por cima de curadoria humana — e mostrar na tela quem foi pulado** | impede que um classificador atropele decisão de gente |

### ⚠️ E três alertas duros, dirigidos aos 224 italianos

**(a) Já existem TRÊS taxonomias paralelas de "quem é esta pessoa" no Brasil** —
`fontes.tipo` (20 valores), `fontes.camada` (5) e `vozes.tipo` (5, **diferentes**) — mais
duas réguas de papel que nunca foram comparadas entre si. O caminho seguro está escrito:

> **mapear para os 20 valores existentes · gravar o esquema italiano AO LADO como
> proveniência · deixar NULO o que não couber**

É exatamente o que `scripts/sensor_mapear_brasil.py` faz.

**(b) `camada` foi derivada de `tipo`** — então o default `creator` **já virou** camada
`produtor` = *"a VOZ do campo"*. Taxonomia nova derivada de taxonomia contaminada
**propaga o defeito em vez de consertá-lo**.

**(c) ⛔ TODO o vocabulário de classificação brasileiro é PT-BR chumbado em regex e NÃO
transfere.** A auditoria mediu que 5 de 60 casos não têm nenhuma palavra do português, e
que isso deflaciona as taxas por um fator **não medido e não uniforme**.

> Isto decide o escopo do reúso: a Itália herda o **CONTRATO** (tabelas, colunas, estados,
> leis) e **não herda os classificadores**. Quem tentar reusar o regex brasileiro em
> italiano vai medir uma cobertura que não existe.

### O defeito brasileiro que mais se parece com a camada italiana

**D9 — a ficha do CANAL respondendo por quem COMENTA:** *18.954 comentários de 389 fontes
técnicas foram contados como fala do técnico, quando são a plateia.* É o mesmo erro de
categoria que a Itália cometeria ao tratar um canal como se fosse a pessoa.


---

## 5 · IDENTIDADE — a resposta definitiva sobre o ORCID

A pergunta era: *a Itália exige ORCID para um pesquisador entrar; o Brasil faz o mesmo?*

> ### ⛔ NÃO. E não é omissão — é doutrina.

**O Brasil não tem coluna de ORCID. Nem de Lattes.** Não há CHECK, não há validação de
formato, não há regex. ORCID aparece **uma única vez em todo o repositório**, como um valor
de `fontes.url` (`fontes-pesquisa-07-08.sql:179`).

Nas 36 linhas de cadastro de pesquisador de 07/08, das 35 URLs legíveis:

```
29  página institucional / pessoal
 3  Lattes
 1  ORCID          ← 2,9%
 1  Google Scholar
```

**O que o Brasil trata como identidade é o ENDEREÇO OBSERVÁVEL DA CONTA NA PLATAFORMA** —
`fontes.external_id`, com dono único em `identidade_da_conta.external_id_de`
(`identidade_da_conta.py:69-104`), e precedência declarada:

```
canal do YouTube (UC+22)  >  @ limpo (instagram/tiktok)
>  URL canônica sem /posts (linkedin)  >  URL canônica COM caminho (web)
```

Lattes, ORCID, Google Scholar, página da Embrapa e site de laboratório entram **todos pela
mesma porta**: são `fontes.url` com `plataforma='web'`.

> ### A frase que decide a questão italiana
>
> **Identificador é PROVA-ENTRE-VÁRIAS, nunca catraca de entrada.**

E há três camadas de id, que não são a mesma coisa:

| camada | o que é | estabilidade |
|---|---|---|
| `fontes.id` (bigserial) | a chave operacional de tudo; `documentos.fonte_id` aponta para ela | **imune** a mudança de nome ou instituição |
| `fontes.external_id` | identidade física da conta, derivada do endereço | estável se o nome mudar; **instável se o endereço mudar** |
| `entidades.chave` | `'id:' + min(external_id do grupo)` | muda se o grupo ganhar um id menor — a própria casa declara |

**A lei da casa:** *"nome é atributo de tela, nunca chave de operação"* — e existe uma
**trava por AST** que a fiscaliza (`provar-fonte-por-id.py:96,144-167`). Ela nasceu de um
defeito medido: `ronda-youtube.py` escolhia a fonte por id, mandava o **nome** adiante, e o
próximo programa pegava a primeira homônima. *"Quatro das cinco frentes de YouTube ficaram
vermelhas por dias."*

### ⛔ O que isso significa para o `SENSOR_ID` italiano

```python
SENSOR_ID = sha1(NOME + '|' + ORGANIZAÇÃO)[:10]
```

**Ele é exatamente o que a lei brasileira proíbe, e a auditoria já mediu o efeito** —
5 de 8 casos adversariais de identidade quebram:

| caso | resultado |
|---|---|
| acento (`Marzachì` / `Marzachi`) | ✅ mesmo id |
| caixa | ✅ mesmo id |
| **travessão U+2010 vs hífen ASCII** | ⛔ **ids diferentes** |
| **espaço duplo** | ⛔ **ids diferentes** |
| **`F. Quaglino` vs `Fabio Quaglino`** | ⛔ **ids diferentes** |
| **`Antonio F Logrieco` vs `Antonio Francesco Logrieco`** | ⛔ **ids diferentes** |
| **mudança de instituição** | ⛔ **id novo — o sensor "morre" e "renasce"** |
| homônimo na mesma organização | ⛔ **colisão: dois humanos, um id** |

E o travessão U+2010 é o mais constrangedor: **o próprio repositório italiano já resolve
esse caractere** em `sensor_canal_identidade.py` e em `speaker_identidade.py::_chave()`.
O `SENSOR_ID` não reusou o contrato que a casa já tinha.

> Hoje o registro tem **0 duplicatas reais e 224 ids únicos** — porque veio de **uma rota
> numa execução só**. A instabilidade é **latente**, e dispara na segunda rota ou na
> segunda execução. É a diferença entre descoberta pontual e fundação de coleta contínua.

---

## 6 · GEOGRAFIA — o Brasil tem quatro espécies; a Itália tem uma

`CLAUDE.md:1566-1571` mais os SQL que já executaram:

| espécie | o que é |
|---|---|
| **BASE** | onde a fonte está sediada |
| **OPERATING** | onde ela atua |
| **INFLUENCE** | onde a audiência aparece |
| **FACT** | onde o fato ocorreu (`geografia-da-fonte.sql:68-73` · `local_do_fato`) |
| *(a quinta, mais fraca)* | a praça do **canal** (`documentos.praca`) |

Mais duas colunas que a Itália não tem:

- **`origem_local`** — a procedência do lugar, com ordem de confiança declarada:
  `declaracao > perfil > nome_canal > video > leitura > audiencia > desconhecida`
- **`evidencia_local`** — a prova textual
- e um **CHECK** (`fontes_local_tem_origem`) que **impede gravar lugar sem dizer como se soube**

> ⚠️ **Armadilha de leitura:** `ACHADO-praca-do-canal-nao-e-praca-da-lavoura.md` é o
> **diagnóstico de 03/08**, não o estado atual. O que ele pedia já foi feito. Ler o achado
> como estado presente é o erro que a Itália deve evitar.

**Reutilizável: os CAMPOS. Não reutilizável: os VALORES** (sul/sudeste/cerrado/matopiba são
do agro brasileiro). A Itália troca os valores, nunca os campos.

O `REGION_BASIS` italiano (`INSTITUTION_ADDRESS_DECLARED_IN_AFFILIATION`) é **BASE com
`origem_local = perfil`**. A Itália não tem OPERATING, não tem INFLUENCE e não tem FACT.

---

## 7 · ALCANCE E RECORRÊNCIA — aqui a Itália acertou, e o Brasil foi além

A pergunta era: *a Itália guarda `AUDIENCE_SIZE` e não usa em regra nenhuma; o Brasil faz igual?*

**Sim, no caminho vivo.** `fontes.alcance` é coletado e atualizado, e **não entra em regra
nenhuma** que decida coleta ou qualidade — medido:

- `fila.peso_de` (`fila.py:629-674`) ordena a fila por cinco fatores; `grep alcance fila.py` dá **zero**
- `relevancia.py` **pede a coluna no select e nunca a usa**

**Mas o Brasil construiu um eixo separado e declarado**: `alcance.py` grava
`relevancia_alcance` (0-100, em 4 partes), com a doutrina de por que ele **nunca** se funde
com a nota de conversa:

> *"Pierobon tira 13 na primeira e 84 na segunda… média entre 'alcança 334 mil pessoas' e
> 'fala de manejo 1,8% do tempo' não significa nada."*

⚠️ E `alcance.py` **não está em workflow nenhum** — o eixo foi desenhado, construído e
**não automatizado**.

**Recorrência**: a régua brasileira é dura e a Itália deve herdá-la:
`MIN_DOCUMENTOS = 3` — *"um documento não é um sinal"* (`radar-do-campo.py:107-108`);
piso de 20 menções + corte de 5% para uma fonte ganhar uma cultura
(`lavoura-da-fonte.py:70,77`); teto de 30% por fonte; **"empate não é especialidade"**.

**Cadência**: `cadencia_dias` é **digitada, não derivada** — 100% das 4.543 fichas preenchidas.

---

## 8 · O MAPEAMENTO — os 224 italianos no contrato brasileiro

Executado por `scripts/sensor_mapear_brasil.py`. Artefato:
[`MAPA-BRASIL.json`](../../data/samples/IT-HUMAN-SENSORS/MAPA-BRASIL.json).

```
224 sensores italianos  →  190 entidades  +  115 fontes
```

**Os 224 nunca foram 224 origens.** Eram origens e canais misturados na mesma linha —
o defeito que `PLANO-entidade-e-fonte.md` nomeia, reproduzido na Itália.

| `entidades.tipo` | n |
|---|---:|
| pessoa | 134 |
| orgao | 38 |
| cooperativa | 10 |
| veiculo | 5 |
| empresa | 3 |

| `fontes.tipo` (vocabulário BR) | n | família |
|---|---:|---|
| tecnico | 34 | B · AGRÔNOMO |
| instituicao | 27 | A · CIÊNCIA |
| orgao_publico | 14 | FORA_DAS_CINCO |
| produtor | 13 | D · CAMPO |
| cooperativa | 12 | E · MERCADO |
| portal | 5 | FORA_DAS_CINCO |
| pesquisador | 4 | A · CIÊNCIA |
| associacao · laboratorio · empresa | 3 · 2 · 1 | — |

**Dez dos 20 tipos brasileiros a Itália não usa:** `creator` · `imprensa` · `podcast` ·
`revenda` · `distribuidor` · `congresso` · `comercial` · `operador` · `estudante` ·
`comite_tecnico`. Os quatro que mais doem são **`revenda`/`distribuidor`** (o canal
comercial), **`comercial`** (o RTV) e **`comite_tecnico`** (FRAC/IRAC/HRAC — resistência).

### Perdas declaradas na tradução

| Itália distingue | Brasil funde | consequência |
|---|---|---|
| AGRONOMIST · TECHNICAL_ADVISER · FIELD_TECHNICIAN · CROP_PROTECTION | `tecnico` | a distinção italiana se perde |
| PLANT_HEALTH_SERVICE · PHYTOSANITARY_CONSORTIUM | `orgao_publico` | serviço regional e consórcio provincial viram um valor |
| UNIVERSITY · PUBLIC_RESEARCH · RESEARCH_CENTRE | `instituicao` | universidade, centro nacional e fundação viram o mesmo |

### O duplicado que o contrato brasileiro expõe na hora

**Fondazione Edmund Mach aparece DUAS vezes** nos 224:

```
web:fmach.it              (rota institucional)   → uma "entidade"
youtube:@fondazionemach   (rota de canal)        → outra "entidade"
```

No contrato brasileiro isso é `MESMA_ENTIDADE`: **uma entidade, duas fontes**. A Itália não
tem resolução de entidade entre rotas, e por isso partiu uma organização em dois sensores.

---

## 9 · O QUE O ENRIQUECIMENTO MEDIU — e o número que decide tudo

| família BR | total | c/ canal | 2+ canais | rede social | CROP | ISSUE | REGION | **monitorável hoje** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **(sem fonte)** | **135** | **0** | 0 | **0** | 135 | 135 | 132 | **0** |
| tecnico | 20 | 20 | 8 | 20 | 20 | 20 | 0 | **20** |
| instituicao | 20 | 20 | 4 | 6 | 20 | 6 | 14 | 6 |
| orgao_publico | 14 | 14 | 0 | 0 | 14 | 0 | 14 | 0 |
| cooperativa | 12 | 12 | 0 | 2 | 12 | 2 | 10 | 2 |
| produtor | 9 | 9 | 3 | 9 | 9 | 9 | 0 | **9** |
| portal | 5 | 5 | 0 | 0 | 5 | 0 | 5 | 0 |
| pesquisador | 3 | 3 | 1 | 3 | 3 | 3 | 0 | **3** |
| associacao · laboratorio · empresa | 6 | 6 | 0 | 0 | 6 | 0 | 6 | 0 |
| **TOTAL** | **224** | **89** | **16** | **40** | 224 | 175 | 181 | **40** |

> # ⛔ 40 de 224 são monitoráveis hoje. 18%.
>
> E **135 das 224 origens — os pesquisadores — têm ZERO canais.** O único "endereço" deles
> é uma URL de busca do Europe PMC, que **não é um canal**: não tem `external_id`, não tem
> conteúdo próprio e não se pode bater nela.

### Papéis multivalorados: o modelo italiano é exclusivo na prática

```
1 papel: 208 sensores    2 papéis: 15    3 papéis: 1
```

Só **16 de 224** têm mais de um papel — e **todos os 16 vêm de `AMBIGUOUS:`**, que é
ambiguidade de leitura, **não prova de dois papéis**. Multivaloração real: **zero**.

### Os casos híbridos que o usuário mandou testar

| caso | estado | n |
|---|---|---:|
| ORGANIZAÇÃO + MÚLTIPLOS CANAIS | **PRESENTE** | 16 |
| AGRÔNOMO + presença pública | **PRESENTE** | 15 |
| PRODUTOR + presença pública | **PRESENTE** | 9 |
| **PESQUISADOR + VOZ SOCIAL** | ⛔ **AUSENTE** | **0** |

> **O zero é o achado.** A pergunta mais valiosa da missão — *"este pesquisador que aparece
> repetidamente na literatura também fala publicamente sobre o mesmo problema?"* — **não
> pode ser respondida hoje**, para nenhum dos 135. Não porque a resposta seja não: porque a
> rota que procuraria o canal **nunca foi executada**.

---

## 10 · ⛔ DEFEITOS ITALIANOS QUE O CONTRATO BRASILEIRO EXPÔS

Cinco, e três deles são exatamente as travas que o usuário mandou verificar.

| # | defeito italiano | prova | trava do usuário |
|---|---|---|---|
| **I1** | **`SENSOR_ID` é derivado do NOME** | 5 de 8 casos adversariais quebram; mudança de instituição cria sensor novo | *"nome nunca é chave de operação"* (lei BR, com trava por AST) |
| **I2** | **Origem e canal na mesma linha** | 224 "sensores" = 190 entidades + 115 fontes; Fondazione Edmund Mach conta duas vezes | item 8 do briefing |
| **I3** | **Papel único, sem array e sem prova por papel** | 208 de 224 com um papel; multivaloração real = 0 | *"pessoa não deve perder um papel verdadeiro"* |
| **I4** | **Papel técnico inferido por keyword na descrição** | **Medical Excellence TV** → `RESEARCH_ORGANIZATION` (casou "ricerca"); **Archivio Nazionale Cinema Impresa** → idem; **W&A Gardens: giardinaggio** → `ENTOMOLOGIST`; **Orto Da Coltivare** (horta de hobby) → `AGRONOMIST` | *"organização não pode virar pessoa técnica por keyword"* |
| **I5** | **Portal classificado como profissão** | **AgroNotizie** → `AGRONOMIST`; no Brasil seria `portal` | *"portal que entrevista agrônomos não vira agrônomo"* |

E dois defeitos de esquema que só aparecem ao tentar caber no contrato:

- **`entidades.nome_canonico` é NOT NULL** — os 40 sensores vindos de canal têm
  `ORGANIZATION = 'NÃO SEI'`, com o nome do canal escondido em `PROVENANCE`. **Não teriam
  nome para inserir.**
- **33 sensores são fonte sem entidade** (`PERSON_OR_ORGANIZATION_NOT_DECLARED`) — no
  contrato brasileiro são `NAO_RESOLVIDA`, e **não deveriam contar como origem qualificada**.

---

## 11 · A TABELA QUE O USUÁRIO PEDIU — família por família

| família | Brasil | Itália hoje | contrato compatível? | campos ausentes | rota ausente |
|---|---|---|---|---|---|
| **pesquisadores** | `pesquisador` (410 fichas) → A·CIÊNCIA | 135 pessoas, **0 canais** | **SIM** | `external_id`, qualquer canal | ⛔ **canal público do pesquisador** |
| **técnicos/agronômicos** | `tecnico` (710) → B·AGRÔNOMO; agrônomo e consultor **dobrados dentro** | 34 fontes, 20 com rede social | **PARCIAL** — a Itália distingue o que o Brasil funde | `REGION` (0 de 20) | melhorar, não criar |
| **produtores** | `produtor` (124, só 2,7%) → D·CAMPO | 13 fontes, 9 com rede social | **SIM** | `REGION`, `onde produz` | ⛔ associações e OP regionais |
| **cooperativas** | `cooperativa` (46) → E·MERCADO ⚠️ mas três vocabulários discordam | 12 fontes, 2 com rede social | **PARCIAL** | rede social | ⛔ canais sociais das cooperativas |
| **distribuidores/canal** | `revenda` (19) + `distribuidor` (0, recusa deliberada) | **ZERO** | **SIM** (vazio dos dois lados) | tudo | ⛔ **rota inteira ausente** |
| **creators/comunicadores** | `creator` (2.491 = 54,8%, gaveta padrão) | **ZERO** — e isso é bom | **SIM** | — | ⛔ mas presença pública precisa virar dimensão |
| **instituições** | `instituicao` (⚠️ fora de DO_CAMPO) | 27 fontes | **SIM** | `ISSUE` (6 de 20) | — |
| **mídia técnica** | `portal` · `imprensa` · `podcast` | 5 fontes como `portal` | **SIM** | — | — |

### A Itália consegue entrar no mesmo motor do Brasil?

> # SIM — mas não do jeito que está.

O contrato serve inteiro. O que não serve é o **formato atual do registro italiano**:
`SENSOR_ID` derivado de nome, origem e canal na mesma linha, papel único sem prova por
papel, e 33 fontes sem entidade. São **quatro correções de esquema**, nenhuma delas
exigindo nova descoberta.

---

## 12 · O QUE FALTA — e as rotas que ainda não foram executadas

**Nenhuma destas foi executada nesta rodada.** São identificadas e provadas como diferentes
do Europe PMC, que é um índice de ciências da vida e não alcança nenhuma delas.

| # | rota | acha o quê | por que é diferente do Europe PMC | custo |
|---|---|---|---|---|
| **R1** | **Canal público do pesquisador** — ORCID `researcher-urls` + página institucional + busca LinkedIn/YouTube pelo nome **com corroboração de instituição** | fecha `PESQUISADOR + VOZ SOCIAL`, hoje 0 de 135 | o EPMC indexa artigos, não perfis | baixo, rota gratuita |
| **R2** | **Malherbologia italiana** — SIRFI (soc. italiana), atas, `Rivista di Agronomia` | os `CEREAL` e `SUGAR_BEET` que faltam | EPMC deu 21 hits em `GRASS_WEEDS` contra 791 em `FLAVESCENCE_DOREE` | médio |
| **R3** | **Revenda / distribuição** — consorzi agrari, rivenditori, Agrofarma | a família `revenda`/`distribuidor`, **hoje zero** | não publica artigo científico | médio |
| **R4** | **Bollettini assinados** — PDFs dos serviços regionais | técnicos **nomeados**, hoje só o serviço | não indexado em lugar nenhum | médio |
| **R5** | **Instagram/Facebook de cooperativa e OP** | produtores e cooperativas com voz | rede social não é literatura | exige `APIFY_TOKEN` |
| **R6** | **`comite_tecnico`** — FRAC/IRAC/HRAC Itália | resistência, que é alvo ADAMA direto | comitê publica recomendação, não paper | baixo |

---

## VEREDITO

```
SAME_ARCHITECTURE_AS_BRASIL            = NÃO  (hoje) → SIM  (alcançável)
READY_FOR_SOCIAL_ENRICHMENT_COLLECTION = NÃO
```

**`SAME_ARCHITECTURE = NÃO` hoje**, e a incompatibilidade é exata e curta:
`SENSOR_ID` derivado de nome · origem e canal na mesma linha · papel único · 33 fontes sem
entidade. **Nenhuma delas exige nova descoberta para consertar** — as quatro são
transformação do que já está gravado.

**`READY_FOR_SOCIAL_ENRICHMENT_COLLECTION = NÃO`**, e a razão é numérica, não de opinião:

- **40 de 224 origens (18%) são monitoráveis hoje.** As outras 184 não têm onde bater.
- **135 pesquisadores têm zero canais** — e é justamente sobre eles que o enriquecimento
  social seria mais valioso.
- Rodar coleta social agora atingiria 40 origens e **declararia cobertura de 224**.

**O que ficou pronto e é permanente:** o contrato brasileiro lido do código vivo e não da
documentação; os 224 traduzidos para `entidades` + `fontes` sem inventar taxonomia; a
medição de canal por família; as fichas ricas; e a lista nomeada dos cinco defeitos
italianos e dos nove brasileiros — com a Itália instruída a **não propagar** os nove.
