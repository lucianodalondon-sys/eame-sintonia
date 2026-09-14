# OS TREZE CORPOS FORA DO FLUXO — DECISÃO

`DECIDE != IMPLEMENT`. Nada foi recolhido, reingerido ou corrigido.

## A resposta

```
LEGACY_KEEP_OUT_OF_FLOW            13
```

Os treze ficam **preservados e fora da Collection operacional**.

> PRESERVAR NÃO É ADMITIR.  
> São duas perguntas, e nenhuma disposição manda apagar corpo nenhum.

## Por que não é uma disposição melhor

| alternativa | porque não |
|---|---|
| `CANONICAL_EQUIVALENT_ALREADY_EXISTS` | nenhum dos 13 tem bytes iguais a uma observação canônica. Medido: 0 de 13. |
| `RECOLLECT_FROM_SOURCE` | exigiria saber o endereço deste documento, e ele viveria na observação que falta. |
| `LEGACY_IMPORT_WITH_CURRENT_PROVENANCE` | o contrato de hoje não separa proveniência da importação atual da aquisição histórica. Sem essa separação escrita, não autorizo. |
| `UNRESOLVED` | os corpos existem no disco e a evidência é suficiente para classificar. |

## O que se mediu em cada um

| item | formato | pista do caminho | conteúdo identifica? | aquisição provada |
|---|---|---|---|---|
| `46622` | SEM_EXTENSAO | IT-T10-002 | sim | **não** |
| `46647` | SEM_EXTENSAO | IT-T10-002 | sim | **não** |
| `91515` | SEM_EXTENSAO | IT-T5-002 | não | **não** |
| `NHEOWL0500_00.html` | HTML | IT-T2-004 | não | **não** |
| `RAW-144fdb152b1a6ae4.txt` | PDF | IT-T2-001 | sim | **não** |
| `RAW-178ebe9e0ea7dd83.txt` | PDF | IT-T3-008 | sim | **não** |
| `RAW-2a12cb316622a9a5.txt` | PDF | IT-T5-003 | não | **não** |
| `RAW-3e941738599367d7.txt` | PDF | IT-T3-010 | não | **não** |
| `RAW-3ef48aaa830edf3b.txt` | PDF | IT-T3-008 | sim | **não** |
| `RAW-445e41701f737d73.txt` | PDF | IT-T2-001 | sim | **não** |
| `RAW-924aabd94168c53a.txt` | PDF | IT-T5-003 | não | **não** |
| `RAW-a927e846ba8e78b0.txt` | PDF | IT-T4-001 | não | **não** |
| `RAW-e5176df66216dfd0.txt` | PDF | IT-T3-011 | sim | **não** |

## A distinção que decidiu tudo

```
CONTENT_PROVES_PUBLISHER != ACQUISITION_PROVENANCE_PROVEN
```

Sete dos treze documentos dizem quem os publicou, dentro do próprio texto.
Nenhum diz que **esta cópia** foi adquirida dali, por quem, quando ou como.
São dois factos e podem divergir.

## Por que a recoleta ficou `NÃO SEI` em todos

A sonda externa tocou o sítio de cada fonte. Isso mede a instituição, não o
ficheiro.

> SABER ONDE FICA A BIBLIOTECA  
> NÃO É SABER QUE LIVRO SE FOI LÁ BUSCAR.

Para voltar a buscar seria preciso o endereço deste documento, e ele viveria
na observação que nunca existiu.

## O estudo externo

| sistema | família | achado |
|---|---|---|
| [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) | modelo de proveniencia | uma entidade pode ser afirmada SEM `wasGeneratedBy`. A atribuicao a um agente aplica-se «quando a actividade nao e conhecida, ou e irrelevante». Ha ma |
| [Archivematica / pratica arquivistica](https://www.archivematica.org/en/docs/archivematica-1.16/user-manual/transfer/transfer/) | preservacao digital | material transferido pode ficar em BACKLOG: guardado, sujeito a avaliacao, e EXPLICITAMENTE ainda nao um AIP. Na descricao arquivistica, «immediate so |
| [Apache Beam](https://beam.apache.org/documentation/programming-guide/) | processamento de dados / streaming | quando a fonte nao da tempo do evento, atribui-se um sentinela (`Long.MIN_VALUE`) — nunca um valor inventado. So se atribui tempo quando ele e extraiv |

**Convergência.** preservar o corpo — nenhum manda apagar; registar honestamente o evento de custodia ACTUAL; nunca fabricar a aquisicao original; manter o desconhecido marcado como desconhecido, com campo proprio em vez de um valor plausivel.

**Divergência.** o arquivo ADMITE o objecto na coleccao com historia custodial desconhecida, porque a funcao dele E a custodia; o sistema de dados MANTEM-NO fora da semantica operacional, porque as contas a jusante dependem da proveniencia.

A Collection nao e um arquivo de custodia: e uma cadeia de evidencia onde a decisao a jusante depende da origem. Por isso vale a postura dos dois lados — guardar o corpo como o arquivo guarda, e mante-lo fora da operacao como o sistema de dados mantem.

## O contrato

```
EXISTING_CONTRACT_SUFFICIENT = PARTIAL
BIBLE_CHANGE_REQUIRED        = NO
CONTRACT_CHANGE_REQUIRED     = YES
```

**A pergunta que não tem dono hoje:**

> Qual e o estado canonico de um CORPO QUE EXISTE e cuja AQUISICAO nunca foi registada — isto e, que nunca teve observacao nenhuma?

`raw_asset.identity_state` (migration 026) tem tres estados e os TRES pressupoem uma LINHA em `raw_asset`. LEGACY_PRE_IDEMPOTENCY e para observacoes que ja la estavam no corte; estes treze nao estao no corte, estao antes da porta. Um estado para linhas nao classifica quem nao tem linha.

**A Bíblia não muda.** Nenhuma lei existente esta errada. COL-LAW-045 ja obriga a coleta manual a entrar pelo contrato; ela nao autoriza nem proibe o corpo que entrou ANTES dela existir. Falta um estado, e nao uma lei nova — e um estado que so se escreve depois de haver um dono para ele.

## Onde estão os números

- `data/derivados/OUT-OF-FLOW-LEGACY-DECISION-V1.json` — ficha por corpo
- `provas/o_legado_fora_do_fluxo.py` — a medição e a decisão
- `tests/test_legado_fora_do_fluxo.py` — 20 testes, 12 mutantes, 0 sobreviventes
