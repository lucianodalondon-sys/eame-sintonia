# DELTA PARA O KNOW-HOW CANÓNICO — O CAMPO QUE O DONO ESCREVE E A PORTA NÃO LEVA

```
ORIGEM            C-COLLECTION-TO-WAITING-ROOM-V1
BRANCH            claude/collection-to-waiting-room-v1
BASE FUNCIONAL    claude/system-map-current-collection-truth-v2 @ 2e73fc1f
KNOW_HOW_MEDIDO   claude/sintonia-eame-know-how-v1 @ 4208fd05   (medido 2026-09-14)
ÚLTIMA SECÇÃO     §118   (medida agora, não herdada)
NÚMERO DESTA      **por atribuir** — quem integrar escolhe o primeiro livre
```

> **⚠️ ESTE FICHEIRO NÃO É UM SEGUNDO KNOW-HOW.**
> O know-how canónico é `SINTONIA-EAME-KNOW-HOW.md`, e ele vive noutra linha.
> Escrever aqui uma cópia das suas leis criaria a coisa que este projeto passa
> a vida a consertar: **dois donos do mesmo conceito**. Isto é um DELTA, na
> forma que `handoff/KNOW-HOW-DELTA-A-BASE-DA-AUDITORIA.md` já fixou.

---

## PRIMEIRO: O QUE A MISSÃO ANTERIOR PEDIU PARA RE-MEDIR

O prompt desta missão nomeou cinco leis e perguntou se ainda são verdade.
Foram medidas contra **esta** árvore, que é outra — outro código, outro banco,
outro ambiente de rede.

| lei | veredito | como se re-mediu |
|---|---|---|
| `REGRA ESCRITA != REGRA EXECUTADA` | **DURÁVEL — e cobrou-se duas vezes** | `CONTRATOS.json` escreve «nenhuma fase paga roda com ALL_APPROVED = NO» e nenhuma fase paga o consultava. E o contrato da fronteira STRUCTURED, depois de escrito, só passou a valer quando `pela_porta` o **chamou** |
| `PRODUTOR E CONSUMIDOR SEM CONTRATO PARTILHADO PERDEM DADO SEM DAR ERRO` | **DURÁVEL — e é a lei central desta missão** | três campos, três fronteiras, três paragens da estrada. Ver abaixo |
| `UM FICHEIRO STRUCTURED QUE NINGUÉM ENTREGA À ADMISSÃO NÃO ESTÁ NO FLUXO` | **DURÁVEL — e mede-se agora** | o vídeo escreve em `REEL-TRANSCRICOES`, a receita nomeia a pasta em `larga_em`, e o `retorno` não declara nada lá. `VIDEO_OUTPUT_HAS_CONSUMER = NO`, medido |
| `LOCAL PATH != REMOTE DURABILITY` | **DURÁVEL** | 25 observações `LOCAL_ONLY` continuam a declarar `RAW_OBJECT_CREATED: true`. Classificadas, não consertadas |
| `READY != WAITING ROOM` | **DURÁVEL** | `admissao.PRONTO` é o estado do CONTRATO; `sala.A_ESPERA` é o estado da FILA. Migration 031 dá-lhes colunas diferentes de propósito |

---

## A LEI DESTA MISSÃO

Três campos pararam a estrada, em três fronteiras diferentes, e os três tinham
a mesma forma: **o dono mediu, escreveu e guardou — e a porta seguinte não
levou**.

```
UM CAMPO QUE O DONO ESCREVEU E A PORTA NÃO LEVA
É UM CAMPO QUE, PARA QUEM ESTÁ DO OUTRO LADO, NÃO EXISTE.
```

Ela já estava escrita nesta casa, em `guarda/preservar_coleta.py`, sobre o
`media_type`. **Uma coluna ao lado, o mesmo defeito, e ninguém o viu** — porque
um campo que não atravessa não dá erro: dá `NAO SEI`, que parece honestidade.

| campo | onde morria | o que custou |
|---|---|---|
| `raw_asset.source_id` | `observacoes_confirmadas()` | perguntava-se à CORRIDA de que fonte era cada documento. Uma corrida que colheu sete fontes **não tem uma** — e `preservar_documento` recusou os sete com «o documento não diz de que fonte veio». `STRUCTURED = 0` |
| `raw_asset.captured_at` | a mesma porta | sete unidades chegaram à Sala com `CAPTURED_AT = NAO SEI`, com o valor medido três degraus atrás |
| `COLLECTED_AT` do coletor | `DO_COLETOR`, que não tinha campo para ele | o livro italiano sabia a hora real da captura e **não tinha por onde a dizer**. A ficha enchia com o `STARTED_AT` da corrida |

### E o corolário, que é o que torna isto difícil de ver

```
DOIS VALORES QUE COINCIDEM POR ACIDENTE
ESCONDEM A FRONTEIRA ONDE UM DELES SE PERDE.
```

`COLLECTED_AT` e `STARTED_AT` são **iguais** enquanto a corrida que colhe for a
corrida que preserva. Só divergem no reprocessamento — e foi por isso que o
defeito sobreviveu a todas as colheitas novas. Medido: capturado a
`2026-09-07`, a Sala dizia `2026-09-14`, **com ar de medido**.

---

## A SEGUNDA LEI: A CONFERÊNCIA QUE ARREDONDA

Ao corrigir o `captured_at`, a conferência campo-a-campo **rejeitou as dez
observações boas**. O leitor formatava `timestamptz` cortando em segundos: a
coluna guardava `15:37:40.362`, ele devolvia `15:37:40Z`.

```
UM LEITOR QUE ARREDONDA FAZ A CONFERÊNCIA COMPARAR
O QUE FOI ESCRITO COM O QUE ELE PRÓPRIO DEIXOU PASSAR.
```

O comentário em cima da linha avisava que «conflito falso ensina toda a gente a
ignorar o alarme» — e era **o próprio formato** que o produzia.

---

## A TERCEIRA LEI: A SALA ESCREVIA E NÃO LIA

`pousar()` funcionava. `listar_pendentes()` funcionava. `ler()` rebentava com
`IndexError` — porque separava campos por `\x1f` e **linhas pelo fim-de-linha**,
e o texto de um READY documental é a extracção de um PDF, com dezenas de
mudanças de linha lá dentro.

```
UMA FILA QUE ACEITA O QUE NÃO SABE DEVOLVER NÃO É UMA FILA.
```

E ao lado, um caractere: com `-R`, o `psql` termina a saída com a mudança de
linha dele, e o **último campo do último registo** vinha com um `\n` a mais.
Chegava para mudar a impressão do conjunto — e pousar de novo exactamente o
mesmo conteúdo lido de volta dava `RUN_ID_CONFLICT`.

```
UM RETRY LEGÍTIMO ACUSADO DE CONTAR DUAS HISTÓRIAS
É PIOR DO QUE UM RETRY QUE DUPLICA: ENSINA A DESLIGAR A TRAVA.
```

---

## A QUARTA LEI: O NOME QUE MUDA DE DONO

`T7` queria dizer três coisas ao mesmo tempo. E a terceira cópia **escrevia**:
`sources.generated.json` saía a rotular o OpenAlex como «Preço e mercado».

```
UMA CÓPIA QUE ESCREVE NÃO É UMA CÓPIA: É UMA SEGUNDA AUTORIDADE.
UMA CHAVE DE DICIONÁRIO TAMBÉM É UMA DECLARAÇÃO DE TAXONOMIA.
UM NOME QUE MUDA DE DONO LEVA CONSIGO TODOS OS SÍTIOS QUE O CITAVAM.
```

O dono novo **não digita a tabela: lê-a** do Atlas. Sem Atlas legível, levanta —
não cai para cópia de reserva, porque uma cópia de reserva é a tabela seguinte.

E o comentário que estava no sítio errado dizia a coisa certa: «inventar aqui
uma segunda lista criaria duas verdades». Escrito, e depois desobedecido no
mesmo ficheiro.

```
UMA INTENÇÃO ESCRITA NO COMENTÁRIO NÃO É UMA LEI NO CÓDIGO.
```

---

## A QUINTA LEI: O NÚMERO QUE SOBE COM O LÉXICO

Esta casa publicava `85.7%` de acerto da porta nos itens italianos. Medido de
onde vinha: **42 dos 49 entravam na CIÊNCIA por uma palavra — `prova` — que
casava dentro de «ap-PROV-al», em regulamento da UE escrito em INGLÊS.**

Nenhum dos 42 era ciência.

```
UM NÚMERO QUE SOBE COM O LÉXICO MEDE O LÉXICO, E NÃO A PORTA.
```

### E a lei gémea, que me apanhou a mim

Acrescentei `fitosanitario` ao léxico de T3 por parecer obviamente de T3, e
**não o medi contra o gabarito humano antes**. Medido depois: os acertos
**caíram de 6 para 4**, e quatro boletins rotulados `T3_NAO` passaram a `SIM` —
todos pela palavra a aparecer no **rodapé institucional** («Unità Organizzativa
Fitosanitario»).

```
O NOME DE QUEM PUBLICA NÃO É O ASSUNTO DO QUE SE PUBLICA.
```

A regra que o devia ter travado estava escrita **quatro linhas acima, por mim,
no mesmo commit**: «uma palavra que qualquer documento tem não separa documento
nenhum».

```
UM VALOR CONGELADO NÃO SE MOVE PARA ACOMPANHAR UMA MUDANÇA:
MOVE-SE DEPOIS DE A MUDANÇA SE PROVAR INOCENTE.
```

---

## A SEXTA LEI: A GUARDA QUE SÓ VÊ A FORMA

Três guardas desta casa acenderam **na prosa que explicava o defeito** — a
citação da forma errada, escrita para o leitor a reconhecer, contava como a
forma errada.

```
PROIBIR A PALAVRA NÃO É PROIBIR O ACTO.
UMA GUARDA QUE NÃO DISTINGUE A LEI DA EXPLICAÇÃO DA LEI
OBRIGA QUEM CONSERTA A APAGAR A EXPLICAÇÃO — E A EXPLICAÇÃO É METADE DO CONSERTO.
```

E a forma inversa: um mapa de rotas escrito como `{"T2": "...", ...}` é
indistinguível de uma taxonomia para quem só vê a forma.

```
UMA GUARDA QUE SÓ CONSEGUE VER A FORMA
OBRIGA QUEM ESCREVE A ESCOLHER UMA FORMA QUE NÃO MINTA.
```

---

## A SÉTIMA LEI: O ESCOPO DE OUTRA MISSÃO

Duas guardas diziam «esta missão só autorizava mexer em X». Era verdade **da
missão que as escreveu**.

```
UMA GUARDA QUE CITA O ESCOPO DE OUTRA MISSÃO
DEIXA DE MEDIR A CASA E PASSA A MEDIR A MEMÓRIA.
```

E a terceira, `test_a_admission_nao_foi_tocada`, compara a **árvore de trabalho
contra o HEAD** — passa assim que alguém commita.

```
UMA GUARDA QUE MEDE O QUE ESTÁ POR COMMITAR GUARDA O HÁBITO, E NÃO O FICHEIRO.
```

---

## A OITAVA LEI: O SENSOR COM ROUPA DE TESTE

O controlo negativo `N6` afirmava `CADENCE_UNKNOWN+HEALTHY`, e o segundo termo
vinha do último registo do livro — do que a SIAS respondeu da última vez.

```
UMA REGRESSÃO QUE DEPENDE DE UM SERVIDOR DE TERCEIROS ESTAR DE PÉ
NÃO É UMA REGRESSÃO: É UM SENSOR COM ROUPA DE TESTE.
```

E o custo não é o alarme, é a **reacção** ao alarme.

---

## A NONA LEI: NÃO CONSEGUI PERGUNTAR

O portão de contrato que portei da prova de fogo lia `ATOR_NAO_ALCANCADO` como
«o contrato reprovou» — uma afirmação sobre o **ator** feita a partir de um
facto sobre a **rede**. O controlo positivo apanhou-o: «um portão que recusa
tudo não é um portão».

```
UNKNOWN != NO. NÃO CONSEGUI PERGUNTAR NÃO É OUVIR UM NÃO.
```

E o mesmo, na medição do OpenAlex: havia duas maneiras fáceis de responder, e
as duas seriam mentira — repetir o cabeçalho antigo, ou adoptar a medição de
outra sessão como se fosse minha.

```
UMA MEDIÇÃO DE OUTRA MÁQUINA CITADA SEM DATA E SEM DONO
DEIXA DE SER MEDIÇÃO E PASSA A SER BOATO.
HOST_ALCANÇÁVEL != ROTA_GRATUITA != QUOTA_DISPONÍVEL.
```

---

## A DÉCIMA LEI: O CORTE QUE JULGA OUTRO DOCUMENTO

`item["texto"] = texto[:20000]`, num ficheiro cujo cabeçalho promete, em
maiúsculas, «NADA SOME EM SILÊNCIO». 19 de 43 documentos passavam do corte; o
maior perdia 87.5%.

```
UM CORTE SILENCIOSO NÃO PRODUZ UM JULGAMENTO PARCIAL:
PRODUZ UM JULGAMENTO SOBRE OUTRO DOCUMENTO.
```

E o dano é **assimétrico**: o que fica depois do corte nunca reprova nada —
apenas nunca conta. Sete julgamentos mudam quando a porta lê o documento
inteiro, e dois deles eram `NAO`, uma rejeição com prova sobre texto que a
porta nunca viu.

```
UM ARTEFATO INTEIRO COM UM JULGAMENTO PARCIAL
NÃO É UM ARTEFATO PARCIAL: É UMA DECISÃO POR REFAZER.
```

---

## O QUE ESTA MISSÃO **NÃO** APRENDEU, E DIZ QUE NÃO

- **Se a aquisição nova funciona.** A política de egresso desta sessão responde
  `403 CONNECT` a todos os hospedeiros externos. Tudo o que se provou foi
  **reprocessamento** de bytes já colhidos. `FIXTURE PROVA PARSER. SÓ A
  INTERNET PROVA AQUISIÇÃO` — e esta missão não diz ter provado aquisição.
- **Se o vídeo atravessa.** Não há um único byte de vídeo nesta árvore. O
  bloqueio está nomeado; o encanamento **não** foi escrito, porque escrevê-lo
  sem o poder exercitar seria `CAN DO != DID DO`.
- **Se a Sala existe no LIVE.** Não há credencial de produção nesta sessão.
- **Se T2 deve ser admitido.** Já tinha resposta medida nesta árvore (`NÃO`), e
  ela aguenta-se sob o mecanismo novo.
