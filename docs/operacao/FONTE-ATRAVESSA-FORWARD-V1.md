# A FONTE ATRAVESSA — CORREÇÃO DO `READER_GAP`

Corrige apenas o defeito forward medido em `C-MEASURE-SOURCE-ID-WIRING-GAP-V1`.
Os 13 `OUT_OF_FLOW_EVIDENCE` ficam intocados.

## O defeito, reproduzido antes de mexer

```
art.raw_do_disco(pdf, RAIZ, COUNTRY_SCOPE="IT")
  SOURCE_ID         'NAO SEI'
  filho SOURCE_ID   'NAO SEI'
  o recibo da coleta sabia: IT-T2-002, em 6 observações
```

## Onde ficou a correcção

O dono do recibo é `coleta/italy_executor.py`: é ele que o escreve e o lê por
corrida. A pergunta nova vive lá, no dono, e não num índice paralelo.

| peça | o que passou a fazer |
|---|---|
| `italy_executor.fonte_do_conteudo` | responde que fonte o livro registou para estes bytes |
| `executor_texto_de_pdf.fonte_para_o_bruto` | pergunta, e carimba só o `SOURCE_ID` |
| `executor_texto_de_pdf.registar_achado` | conta as três respostas no recibo |

`raw_do_disco` não mudou. A lei que o proíbe de adivinhar continua de pé.

## Porque a chave é o conteúdo, e não o caminho

Medido no livro de hoje, 144 observações:

| campo | presente |
|---|---|
| `RAW_SHA256` | 144 de 144 |
| `RAW_PATH` | 35 de 144 |

E um dos caminhos é `C:/ea...`, absoluto e de outra máquina. Juntar por
caminho responderia «não sei» a três quartos do livro.

> O SHA É A CHAVE QUE ACHA A LINHA.  
> A FONTE VEM DO CAMPO QUE O COLETOR ESCREVEU NELA.

## A travessia forward

Sete cenários, numa coleta encenada e descartável. Nenhum lê produção.

| cenário | resultado |
|---|---|
| 1 · a fonte provada atravessa os quatro estagios | passa |
| 2 · sem recibo continua UNKNOWN, e o caminho nao vota | passa |
| 3 · o livro vence o caminho, e vence por o caminho nao ter voto | passa |
| 4 · sentinela no livro nao vira identidade | passa |
| 5 · duas fontes para o mesmo conteudo nao se desempatam | passa |
| 6 · retry e nova corrida nao mudam a fonte nem a perdem | passa |
| 7 · o ficheiro mudou de nome e de pasta, e a fonte sobreviveu | passa |

```
FORWARD_EXECUTED   = YES
SOURCE_ID_PRESERVED = YES
```

Nos positivos a cadeia avança até `pertence ao universo`: a pergunta da
origem passou a ter resposta, e o documento chega ao tema.

## O que o executor passou a contar

```
PDF italianos olhados ..... 49
fonte vinda do livro ...... 12
sem fonte no livro ........ 37
fonte em CONFLITO ......... 0
```

> UMA CONSULTA QUE NINGUÉM CONTA  
> É INDISTINGUÍVEL DE UMA CONSULTA QUE NÃO ACONTECE.

Os 37 sem fonte são os corpos que entraram por fora do pipeline. São os 13
`OUT_OF_FLOW` desta coorte e os restantes fora dela. Continuam `NÃO SEI`, e
é isso que se espera: `COL-LAW-045` diz que coleta manual entra pelo mesmo
contrato, e nenhuma delas entrou.

## O caminho não ganhou voto

O brief admitia detectar conflito entre caminho e livro. Não implementei
isso na coleta, e a razão é deliberada: para o código discordar do caminho
teria de o ler, e ler o caminho para extrair identidade é exactamente o
padrão proibido. O caminho não é consultado em lado nenhum.

Não há desempate porque não há empate. O cenário 3 prova-o: o caminho diz
`IT-T3-008`, o livro diz outra coisa, e o livro passa sem sequer competir.

## O que não mudou

```
ADMISSION_CHANGED              NO
INGRESS_TRANSLATOR_CHANGED     NO
DERIVATION_SEMANTICS_CHANGED   NO
MIGRATION_CREATED              NO
BACKFILL                       NO
OUT_OF_FLOW_13_CHANGED         NO
SOURCE_ID_INVENTED             NO
```

`admissao/admissao.py`, `coleta/ingresso.py` e `leis/artefato.py` têm zero
linhas de diff. O registo de artefactos e o livro da coleta também.

## Onde estão os números

- `data/derivados/FONTE-ATRAVESSA-FORWARD-V1.json` — os sete cenários
- `provas/a_fonte_atravessa_ate_a_porta.py` — a travessia
- `tests/test_fonte_atravessa.py` — 21 testes, 13 mutantes, 0 sobreviventes
