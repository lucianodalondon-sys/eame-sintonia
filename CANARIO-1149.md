# CANÁRIO-1149 — o primeiro vermelho de `derived:1149`

> D129 do dono: um item REAL coletado automaticamente tem de atravessar até ao portal.
> Item: `derived:1149` · T5 · `IT-T5-111` (CREA) · comunicado «Xylella fastidiosa: dalla ricerca CREA
> nuove strategie per l'olivicoltura». Base: `servico-20260923-0923` = `e24139702` (+ insumos `f952966`).
> Tudo offline. **Nada foi escrito na Sala real.**

## 1 · A causa exata de cada NAO SEI

Reproduzido offline com o texto real (`docs/lab-insumos/canario-1149/LINHA-DA-SALA.json`), pela mesma estrada
do reprocesso (`admissao/reprocessar_tempo_lugar.ready_de`) — saiu **idêntico** à linha da Sala.

| campo | a Sala dizia | causa exata (código) |
|---|---|---|
| **PUBLISHED_AT** | `NAO SEI — JSON-LD … ausente; … INDICE: ausente` | O leitor da publicação (`coleta/executor_texto_de_html.tempo_de_publicacao`) só lê **metadado HTML** (JSON-LD, `article:published_time`, `<time>`, itemprop, índice). A página do CREA não tem nenhum; a data só está no **texto visível** «COMUNICATO STAMPA remove 22 giu 2026». O próprio ficheiro dizia: «ler datas em prosa é outra régua». Não existia. |
| **FACT_LOCATION** (base) | `… o texto não tem corpo (só menu/rodapé)` | O texto guardado é **uma linha só** (menu + comunicado + rodapé achatados, 8.989 letras). `leis/fato_do_texto.corpo` filtra **linha a linha**; a linha única casa `RODAPE` («Seguici», «tel.», «Partita IVA», «Via della Navicella 2/4») e sai **inteira** — o comunicado com ela. |
| **REGIAO_DO_FATO** (janela) | `NAO SEI — o texto nao diz onde o estudo foi feito` | Três faltas em `leis/estudo_chaves.py`: (1) «Salento» não existe em **nenhum** vocabulário (gazetteer só tem regiões/províncias; `ZONAS_IT` só macro-zonas) — nem entra em `RECUSADOS`; (2) «nell**e aree colpite del** Salento» não casa `_PREPOSICAO` (não conhece «nelle aree … del»); (3) «selezionato» não é pista de estudo em `_PISTA_DE_ESTUDO`. |
| **PROBLEMA** | `NAO SEI — D112: 2 problemas (xylella, nematode)` | `leis/boletim_do_campo.declarar_problema` conta toda menção do vocabulário como candidato; «nematod[ie]» está em `PROBLEMAS`. Não havia regra para o organismo que é o **remédio**: «due nuove specie di **nematodi parassiti della sputacchina**». E, com a página achatada, `_onde_esta` chamava tudo de `DOCUMENT_TITLE` com a **página inteira** como BASE. |

## 2 · O conserto — regras GERAIS, nenhum caso especial para 1149

| regra | ficheiro:linha | o que faz |
|---|---|---|
| página achatada | `leis/fato_do_texto.py:203` (`LINHA_ACHATADA = 300`), `:207` `_linhas_do_corpo`, `:230` | Linha com ≥ 300 palavras parte-se em **frases**; cada frase passa pelo MESMO filtro (palavras mínimas + RODAPE). Linhas < 300 não mudam. |
| publicação no texto | `coleta/executor_texto_de_html.py:513` `BASE_TEXTO`, `:530` `publicacao_no_texto`, `:559` `tempo_de_publicacao_com_texto` | **Nível 5, o último**: só fala se JSON-LD/meta/`<time>`/itemprop/índice se calaram. Rótulo colado («COMUNICATO STAMPA», «NEWS», «pubblicato il», «data (di) pubblicazione») + até 2 fichas de interface minúsculas («remove», «event», «|») + «dd mmm aaaa» (mês italiano) ou «dd/mm/aaaa». Duas datas diferentes = AMBÍGUO = NAO SEI. Base = o trecho. **Nunca FACT_TIME.** |
| o texto chega ao leitor | `coleta/italy_executor.py:253` (`texto=`), `:311`; `admissao/reprocessar_tempo_lugar.py:128` | Sem os bytes guardados, o texto da linha ainda responde pelo nível 5. |
| agente de controlo | `leis/boletim_do_campo.py:742` `HOSPEDEIROS_ANIMAIS`, `:754` `agente_de_controle`, `:785` | Menção colada a «parassit… / antagonist… / predator… / entomopatogen… / nemici naturali / per il (bio)controllo / per il contenimento / agenti di (bio)controllo» + preposição + **hospedeiro animal-praga** (praga do vocabulário ou insetto/vettore/sputacchina/philaenus/…) sai de CANDIDATOS e fica em `AGENTES_DE_CONTROLE` com o trecho. Hospedeiro planta («delle piante», «dell'olivo») ⇒ continua PROBLEMA. Vale para boletins e estudos (é o único que preenche PROBLEMA/v1). |
| página achatada ≠ título | `leis/boletim_do_campo.py:686` | O nome numa linha achatada é `TEXT` com o trecho à volta, nunca `DOCUMENT_TITLE` com a página inteira. |
| lugar do estudo | `leis/estudo_chaves.py:101-102` (selezionat/fenotipizzat), `:113` `_AREA_DE`, `:341`; `coleta/pesquisadores_t6.py:292` (`'Salento'`) | «nelle/nella/in (the) aree/zona/territorio [≤2 palavras] del/della/of X»; «selezionato/fenotipizzato» é trabalho de estudo; «Salento» entra como **ZONA** sub-regional. |

### D112 · «aree colpite del Salento» sustenta o quê, e com que granularidade

- **Sustenta o LUGAR DO ESTUDO** (a seleção/caracterização dos 200 genótipos), `KIND = LOCAL_DO_ESTUDO`,
  `PRECISAO = ZONA`, `VALOR = Salento`, BASE = a frase literal. O verbo («selezionato») e o lugar estão na
  mesma frase, com a preposição a reger a área.
- **Não vira Puglia.** Que o Salento fica na Puglia o texto não escreve; a porta não acrescenta (teste L2).
- **Não sustenta `FACT_LOCATION`** (a coluna do item). `FACT_LOCATION` é do LUGAR-FATO (`fato_do_texto` +
  `fato_local`, que se «repuxa da Itália, não se edita aqui»): ele não conhece o Salento e, pela CAP-SCI, a
  seleção de genótipos é trabalho de estudo, não acontecimento de campo. Fica `NAO SEI`, agora com o porquê
  verdadeiro: `(só mencionados: Bari)` — «CIHEAM Bari» é nome de instituição, sem preposição de lugar.
- **O vetor.** *Philaenus spumarius* / sputacchina **não** está no vocabulário de pragas e **não** o acrescentei:
  entraria como segunda praga e o D112 devolveria NAO SEI de novo. Uma relação «VETOR_DE» é decisão do dono.

## 3 · Ensaio num PostgreSQL DESCARTÁVEL (`provas/canario_1149/ensaio_descartavel.py`)

⚠️ O dump da Sala **não está no repositório**. O ensaio sobe um Postgres 16 descartável (base `descartavel`,
trava `guarda/banco_descartavel`), aplica as migrations pela cadeia canónica (**34 PASS**), e semeia a linha
exportada de `derived:1149`; `collection_run` e `raw_asset 2272` entram como **STUB declarado**
(`FORWARD_IDENTITY_UNPROVEN`, `preserved=false` com motivo, sha256 de zeros) só para a FK e o URL do export.

| passo | resultado (`provas/canario_1149/ENSAIO-1149.json`) |
|---|---|
| SECO | código 0 · `GRAVOU_NO_BANCO: false` · impressão da Sala igual antes/depois |
| backup | pg_dump → pg_restore numa 2.ª base → mesmo conteúdo → `PROVA_VALE: true` |
| aplicar **sem** PARAR.flag | **recusado** (código 1) |
| aplicar (com flag + PROVA_VALE) | **5 inseridas** pela porta `rever` |
| aplicar outra vez | **0 inseridas · 5 já eram assim** (idempotente) |
| linha original | intacta (`NAO SEI | NAO SEI`) — só `sala_de_espera_revisao` cresceu |

**A nova revisão de `derived:1149` (vista `sala_de_espera_atual`):**

```
published_at        2026-06-22
published_at_basis  TEXTO: a data escrita ao lado do rotulo de comunicado «COMUNICATO STAMPA remove 22 giu 2026»
fact_time           NAO SEI   (publicação ≠ facto; não revisto sem o livro)
fact_location       NAO SEI   · base: «… no corpo do texto (só mencionados: Bari)»
CULTURA             [olivo, vite]
PROBLEMA            xylella   · VEIO_DE TEXT · ENTITY_SOURCE SPAN · CODIGO NOME_CANONICO
AGENTES_DE_CONTROLE nematode  · «… due nuove specie di nematodi parassiti della sputacchina»
REGIAO_DO_FATO      [Salento] · ZONA · LOCAL_DO_ESTUDO · «Il team di ricerca ha selezionato e caratterizzato,
                                nelle aree colpite del Salento 200 genotipi di olivo, …»
```

## 4 · O motor e o pote sobre a cópia (`motor/motor_das_capacidades.py --hoje 2026-09-28`)

| | ANTES | DEPOIS |
|---|---|---|
| CAP-WIN 1149 | NOT_POSSIBLE · INT-LAW-091: **PROBLEMA** NAO SEI (xylella, nematode) **e** REGIAO NAO SEI | NOT_POSSIBLE · INT-LAW-091: **só REGIAO** NAO SEI |
| D112a (motor) | — | `REGIAO_DO_FATO: VALOR_RECUSADO [Salento]` — «origem ITEM.TEXTO (…ESTUDO-CHAVES-V1) não sustenta lugar do fato» |
| CAP-SCI | FORA: «o FATO não declara DOI, TRIAL_ID nem espécie científica» | igual |
| LINEAGE | PUBLICATION_TIME NAO SEI | **PUBLICATION_TIME 2026-06-22** · FACT_TIME NAO SEI · `PUBLICATION_TIME_NAO_E_FACT_TIME` |
| POTE v2 | 0 objetos · 1149 só em LACUNAS | igual (0 objetos) |
| LIGACAO_ADAMA | NAO_SEI (sem par) | NAO_SEI (sem par). Pela porta, à parte: olivo × xylella (e × sputacchina/Philaenus) = **A_CONFIRMAR** — «nenhuma bula lida liga cultura e alvo; 61 bulas ativas não lidas» |

**Expectativa para a Sala real** depois de aplicar: a mesma coisa — 1149 deixa de ser bloqueado pelo PROBLEMA;
continua NOT_POSSIBLE só pela REGIAO; `PUBLICATION_TIME = 2026-06-22` no LINEAGE.

## 5 · O PRÓXIMO VERMELHO (o porquê honesto)

**Intelligence/triagem ← FATO do item.** O motor está a cumprir a lei:

1. o `FATO` de 1149 é `NAO_SE_APLICA` (a Collection não declara ESPÉCIE, DOI nem TRIAL_ID para um comunicado
   web do T5) ⇒ a triagem **não** o manda para a CAP-SCI ⇒ cai na CAP-WIN (janela de **campo**);
2. na CAP-WIN, a D112a recusa `REGIAO_DO_FATO` porque a origem é o extrator de **estudo** (LOCAL_DO_ESTUDO),
   que não é `ESCRITO/CITADO` de facto de campo — e isso está **certo** pela CAP-SCI («estudo nunca vira
   incidência de campo»). Mudar o `VEIO_DE` para `ESCRITO` faria o Salento-do-estudo virar janela de campo: não fiz.

Decisão que falta (dono/coordenação): **que espécie é um «comunicado de resultados de pesquisa» sem DOI** e
que capacidade o lê — (a) a Collection declara no FATO `ESPECIE = RESULTADO_CIENTIFICO` a partir do texto
(«Presentati i primi risultati dei progetti…») e o item vai para a CAP-SCI com `LOCAL_DO_ESTUDO = Salento`; ou
(b) a Intelligence ganha leitura para comunicados de pesquisa. Sem isso, POTE/CASCO/PORTAL não recebem 1149.

Amarelos vistos no caminho (não bloqueiam este elo, não mexi):
- `CROP_ID` sairia `olivo,vite` (a CAP-WIN cola a lista); o texto nomeia mesmo a vite (NOVIXGEN, Pierce).
- EPPO: `XYLEFA` existe na tabela ES-T4-001 mas fica fora por `es == scientific` (regra anti-gaveta do
  `normalize_agro`), e o `PORQUE_SEM_EPPO` diz «o texto não escreve o binómio» — a frase está errada para este caso.

## 6 · Comando exato para o coordenador (SÓ este item, na Sala real)

```bat
:: 0. exportar SÓ a linha, pela vista, dentro de transação read-only (a mesma query do motor)
set PGOPTIONS=-c default_transaction_read_only=on
psql -X -At "%SALA_DSN%" -c "begin transaction read only;" -f motor\r7_export_da_copia.sql -c "commit;" > C:\Users\London1\sintonia-sala-italia\canario-1149\export-1149.json
set PGOPTIONS=
:: (o export traz todas as linhas; o script escolhe SÓ --item derived:1149 e recusa se houver 0 ou 2+)

:: 1. SECO (não abre banco) — conferir RESUMO e REVISOES
py admissao\reprocessar_um_item.py --entrada C:\Users\London1\sintonia-sala-italia\canario-1149\export-1149.json --item derived:1149 --saida C:\Users\London1\sintonia-sala-italia\canario-1149\revisoes-1149.json

:: 2. parar o bot e provar o backup
type nul > curadoria\PARAR.flag
py scripts\micro_coleta\provar_backup_da_sala.py --saida=C:\Users\London1\sintonia-sala-italia\canario-1149\backup
:: (tem de imprimir "PROVA_VALE": true; grava backup\PROVA-BACKUP-SALA.json com DUMP e PROVA_VALE)

:: 3. APLICAR (Sala canónica; recusa sem PARAR.flag, sem PROVA_VALE, com outra versão do código ou outro texto)
set SINTONIA_SALA_BACKEND=POSTGRES
py admissao\reprocessar_um_item.py --aplicar C:\Users\London1\sintonia-sala-italia\canario-1149\revisoes-1149.json --backup C:\Users\London1\sintonia-sala-italia\canario-1149\backup\PROVA-BACKUP-SALA.json --recibo C:\Users\London1\sintonia-sala-italia\canario-1149\recibo-1149.json

:: 4. soltar o bot
del curadoria\PARAR.flag
```

Saída esperada do passo 3: `"INSERIDAS": 5, "JA_ERAM_ASSIM": 0` (repetido: `0` e `5`).
O `--backup` é o `PROVA-BACKUP-SALA.json` que `provar_backup_da_sala.py` grava na pasta `--saida` (traz `DUMP` e
`PROVA_VALE`, `scripts/micro_coleta/provar_backup_da_sala.py:74-77`). NÃO SEI se o `psql` do Windows aceita
`-c … -f … -c …` na mesma chamada nesta instalação: se não aceitar, correr a query do export numa sessão
`begin transaction read only;` como no RUNBOOK-R7 §2.

## 7 · Provas

- **Testes novos:** `tests/test_canario_1149.py` — 29 (texto real + casos que reprovam: menu/rodapé, plural
  «Comunicati Stampa» de listagem, duas datas, data impossível, metadado continua a ganhar, publicação ≠ facto,
  nematoide-praga, «parassiti delle piante/dell'olivo», «Peronospora: … per il controllo della peronospora»,
  lugar sem verbo de estudo, Salento ≠ Puglia, só um item, as cinco travas do aplicar).
- **Mutação:** `provas/canario_1149/mutacao_1149.py` → **19/19 mortos** (`MUTACAO-1149.json`).
- **Bateria por nome** (`provas/int_r7/bateria_por_nome.py`, rede fechada): ver `provas/canario_1149/BATERIA-*.json`
  e o resumo no fim deste ficheiro.
- **System Map:** regenerado e validado pela cadeia (resumo no fim).

## EM PALAVRAS SIMPLES

A notícia do CREA dizia claramente a data (22 de junho), o lugar (Salento) e a praga (Xylella), mas o sistema
respondia «não sei» às três. Não era má vontade: a página chegou toda colada numa linha só, e o filtro de
rodapé jogava fora a notícia inteira junto com o endereço do CREA; a data estava escrita no texto e o
sistema só procurava data escondida no código da página; «Salento» não estava em nenhuma lista; e os
nematoides — que são os **bichinhos do bem** que atacam o inseto que espalha a Xylella — eram contados como
uma segunda praga, e com duas pragas a regra manda dizer «não sei».

Consertei as quatro regras de forma geral (valem para qualquer notícia, não só esta), com testes que também
provam o contrário (nematoide que ataca a planta continua praga; data de menu não conta). Num banco de
mentira, a correção entrou pela porta certa, sem apagar nada, e o motor agora aceita a praga e vê a data.

O item ainda não chega ao portal: o motor trata-o como «observação de campo», e o Salento é o lugar de um
**estudo**, não de um foco no campo — por isso ele recusa, e com razão. O próximo passo é decidir que
um «comunicado de resultados de pesquisa» é ciência, para ele ir para a gaveta certa.

---

### Resumo das provas (números medidos)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `f952966` (= `e24139702` + insumos) | 332 | 7507 | 131 |
| depois `3f36ead` | 333 | 7536 | 131 |

**Novas: 0. Sumidas: 0.** (`provas/canario_1149/BATERIA-BASE-f952966.json`, `BATERIA-DEPOIS-3f36ead.json`; as 131
são as mesmas da base, pelo nome — nenhum teste foi enfraquecido nem ajustado.) Mutação **19/19 mortos**.
