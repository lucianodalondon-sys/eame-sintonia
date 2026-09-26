# RELATÓRIO — NUVEM-CONCORRENZA-V1

Ramo `nuvem-concorrenza-v1`, base de produção `69b0e23f`. Sem rede externa. Nenhum livro vivo foi
alterado (`curadoria/*-V1.json`, `data/collection-ledger`, `candidatas/FONTES-CANDIDATAS.json` só foram
**lidos**). Dados da Sala: nenhum — só o que está no repo e casos sintéticos marcados `SINTETICO`.

## 1. O que foi feito

### 1.1 A regra que pôs a Didacta em Concorrenza (T9) — achada e consertada

- **Onde errou:** `curadoria/atribuir_source_id.py:87` (antes linha 83), regra `_ENTIDADE` do T9, usada
  pelo QUALIFY do Source Curator (`atribuir_source_id.py:111`) e pelo `gatilho_discovery.py:494`.
- **Dois defeitos na mesma regra:**
  1. lia o **endereço inteiro, com o caminho**. CAND-0412 («Scopri l'evento»,
     `fieradidacta.indire.it/it/visita-didacta-`**`italia`**`-edizione-abruzzo/`) → «italia» → T9 →
     **IT-T9-021**. Motivo gravado no livro: `o nome da fonte diz o que ela E: «italia» -> T9`
     (`curadoria/SOURCE-ID-ALLOCATION-V1.json:3390`).
  2. a forma jurídica não tinha fim de palavra: «**Spa**zioRegione» → S.p.A. → T9 → **IT-T9-022**.
- **Conserto:** `_nome_e_casa()` (`atribuir_source_id.py:91`) — a regra lê o **nome + a casa (host)**,
  nunca o caminho; e `(?![a-z0-9])` no fim da forma jurídica (`:87`).
- **Efeito medido sobre as 597 alocações do livro** (só leitura;
  `data/derivados/CONCORRENZA-V1/TERRITORIO-ANTES-DEPOIS.json`): mudam 27. Leitura minha, uma a uma
  (não é gabarito): **13** errado→certo (ex.: páginas `/ricerca` da Regione Lombardia davam T5),
  **9** errado→`NAO SEI` (inclui Didacta e SpazioRegione), **5** certo→`NAO SEI` (4 páginas da Nomisma,
  1 da Tecnichenuove), **0** certo→errado.
- ⚠️ **Não mexi no livro.** IT-T9-021 e IT-T9-022 continuam com o número que têm: número dado não
  recicla, e mudar a gaveta de uma fonte já numerada é decisão do dono do Atlas. A regra consertada
  vale para as próximas qualificações.
- Fica de fora (observação, não mexido): o vocabulário de admissão T9 (`admissao/admissao.py:1041`,
  «evento», «novita», «fiera») é o que deu SIM à Didacta na régua de relevância. É régua: só se
  mexe com gabarito medido.

### 1.2 O extrator da Concorrenza — `coleta/comunicacao_concorrenza.py` (novo)

Para cada item: **empresa + produto + cultura/problema + lugar + tempo + tipo de comunicação**, com os
nomes que o casco já lê (`italia-portale/client/italy-app-model.js:2352`: `COMPANY`,
`PRODUCTS_PROVED`, `CROP_TERMS`, `ISSUE_TERMS`, `CLAIM_DOMAIN`).

| peça | onde | regra |
|---|---|---|
| empresa que fala | `:96` | só do canal/conta **declarado pela coleta**; empresas citadas no texto vão para `EMPRESAS_NOMEADAS_NO_TEXTO`; ADAMA = `ADAMA_PROPRIA`, nunca concorrente |
| produto | `:138` | só nome com **® ou ™** no texto (mesma prova do pacote); marca de **substância** («a base di Revysol®», «Inatreq™ active», «fungicida con Revysol®») vai para `MARCAS_DE_SUBSTANCIA` |
| cultura/problema | `:182`, `:193` | tabelas de `comunicacao_classificar.py` **lidas de lá** + acréscimo medido nas 561 |
| lugar | `:382` | só o que o texto nomeia; `COUNTRY_REACHED` do anúncio viaja à parte (alcançado ≠ dirigido ≠ lugar do facto) |
| tempo | `:427` | data do anúncio/publicação = `COMMUNICATION_TIME`; `FACT_TIME` = `NAO SEI` sempre (INT-LAW-101) |
| tipo | `:226` | `ANUNCIO_PAGO` · `ORGANICO` · `COMUNICADO` · `REGISTO` · `NAO SEI`, pelo que a coleta declarou; comunicado só com empresa conhecida |
| alegação × facto | `:261`, `:436` | `ALEGACOES` (camada COMUNICACAO — inclui a empresa dizer «autorizzato») e `FACTOS_REGULATORIOS` (só do registo T4) — **duas contagens, nunca somadas** (CAP-COMP, Bíblia §34) |
| tomada T4 | `:287`, `:297`, `:324` | `CONTRATO_DO_REGISTO_T4` (o parser de outra sessão implementa `procurar_por_nome`); estados `REGISTO_NAO_LIGADO` (=NAO SEI, nunca «não registado») · `NAO_ENCONTRADO_NO_REGISTO` · `ENCONTRADO_MESMO_TITULAR` · `ENCONTRADO_OUTRO_TITULAR` · `AMBIGUO_TITULARES_DIFERENTES`; registo ≠ venda (INT-LAW-067) |

**Medida nas 561 atividades de concorrente do repo**
(`build/ITALY-REALITY-HANDOFF-V2/.../competitor-activities.json`;
`data/derivados/CONCORRENZA-V1/MEDIDA-561.json`):

| | valor |
|---|---|
| empresa | 561 / 561 (vem da coleta) |
| tipo | 414 anúncio pago · 147 orgânico |
| com produto | 126 / 561 |
| com cultura | 324 / 561 (213 só com a tabela antiga) |
| com problema | 174 / 561 (76 só com a tabela antiga) |
| com país do facto (texto) | 110 / 561 |
| alegações | 614 · factos regulatórios **0** (nenhum registo ligado — é NAO SEI, não zero de registos) |
| marcas de substância que o pacote contava como produto | 32 |

Limites declarados: produto sem ® não é extraído; «Zorvec» fica produto (a Corteva usa o nome para
substância e produto — só o T4 decide); falso conhecido «semi di soia» numa tinta; o texto do pacote
vem cortado em 700 letras (4 produtos do pacote não estão no texto que o repo guarda).

## 2. Testes — antes / depois, pelo nome

Módulos: `test_comunicacao`, `test_c7_lugar_do_fato`, `test_reel_transcricao`,
`test_scrap_convergencia`, `test_hero_cases_v1` (+ novo `test_comunicacao_concorrenza`).

- **Antes (base 69b0e23f):** 2 falhas —
  `test_todo_artefato_canonico_existe_e_bate` (hero_cases) e `test_zero_colisoes_de_nome_curto`
  (scrap_convergencia, `mutacao.py` em 3 gavetas — herdada).
- **Depois:** as **mesmas 2**, pelo nome. **0 falhas novas.** Novo módulo: **31/31 OK**.
  `test_comunicacao`: as 50 linhas `ok` iguais antes/depois.
- Declarado: na 1.ª tentativa acrescentei as culturas dentro de `comunicacao_classificar.py` e o
  guarda da C7 (`test_os_outros_dois_lugares_nao_foram_tocados`) reprovou. **Não mexi no teste**:
  desfiz a mudança e o acréscimo passou a morar no extrator (`:182`).

## 3. Mutação — `provas/mutacao_concorrenza.py`

**24/24 colhidos.** Um defeito de cada vez; reposição byte a byte (sem `git checkout`); `-B` e
`__pycache__` apagado a cada mutante. Cobre: regra do nome (caminho, fim de palavra, casa), substância
× produto, vírgula × conjunção, empresa adivinhada pelo texto, ADAMA como concorrente, comunicado sem
empresa, orgânico × pago, alegação virando facto, contagens somadas, «sem registo» virando «não
registado», outro titular virando validado, data da comunicação virando data do facto, alcance virando
lugar, acréscimo desligado, «pero» espanhol, lista de marcas divergente do pacote.

## 4. System Map (pela cadeia, com LOCK-PESADO 11:45–11:58)

- Declarado em `system-map/data/architecture.declared.json`: `coleta/comunicacao_concorrenza.py` na
  peça `C-COLETA-PUBLICA`; `provas/mutacao_concorrenza.py` na peça `C-PROVA-COLETA`.
  (1.ª tentativa pus a prova de mutação em `C-COLETA-PUBLICA` e o VALIDAR reprovou
  `P2_PASTA_BATE_COM_MAPA` — pasta `provas/` ≠ peça em `coleta/`. Corrigido e regerado.)
- `correr_a_cadeia.py REGERAR` → `CADEIA=OK` (20/20 passos); gerados commitados.
- `correr_a_cadeia.py VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`**.
- `impressao_da_arvore.py --conferir-carimbo` → **`IMPRESSAO_DO_CARIMBO=IGUAL`**
  (árvore `a020e94c…` sobre 3695 ficheiros-fonte).
- O VALIDAR reescreveu 6 gerados só com HEAD/hora (ruído que se autorreferencia). Guardado antes
  de descartar: `git stash` «nuvem-concorrenza-v1-ruido-do-validar-2f4339b6»
  (`5218c0bcccf99c2651935205cdd20621fa490007`).

## 5. Commits

`e7a2d084` extrator + regra · `611dd54a` mutação · `1069a3f5` relatório · `14efda32` e `2f4339b6`
mapa declarado · `b6629767` mapa regerado · o SHA final é o commit deste relatório (ver a
mensagem de entrega; este ficheiro não pode conter o próprio SHA).

## EM PALAVRAS SIMPLES

- **A Didacta.** Uma feira de escolas foi parar na gaveta "concorrentes". O motivo: a regra olhava o
  endereço inteiro da página e viu a palavra "italia" no meio dele — como achar que alguém é
  italiano porque a rua dele se chama "Rua Itália". Agora a regra olha só o nome e o domínio do site,
  não o caminho da página. Achei um segundo erro na mesma regra: "**Spa**zioRegione" era lido como
  "S.p.A." (empresa). Também consertado.
- **O que isso muda:** das 597 fontes já numeradas, 27 seriam lidas de outro jeito — 13 passam a
  ficar certas, 14 passam a "não sei" (5 destas estavam certas antes). Nenhuma passa de certa para
  errada. As fontes já numeradas **não mudaram**: isso é decisão do dono do Atlas.
- **O extrator.** Para cada anúncio ou vídeo de concorrente ele diz: quem fala, que produto, que
  cultura e que praga, onde, quando e se é anúncio pago, post normal, comunicado ou registo.
- **A regra mais importante:** o que a empresa **diz** ("é eficaz", "é autorizado") fica numa caixa;
  o que o **registo oficial** prova fica noutra. As duas caixas nunca se somam. Como a diferença
  entre a propaganda na caixa do remédio e a bula aprovada.
- **O registo oficial (T4)** ainda não está ligado: outra sessão faz a leitura dele. Deixei a tomada
  pronta; enquanto ninguém liga, a resposta é "não sei", nunca "não registado".
- **Números:** produto achado em 126 de 561 itens; cultura em 324 de 561; praga em 174 de 561. Achei
  32 casos em que o pacote antigo contava a **substância** (ex.: Revysol) como se fosse produto.
- **Provas:** 31 testes novos passam; nenhum teste antigo passou a falhar; plantei 24 defeitos de
  propósito e os testes pegaram os 24.
