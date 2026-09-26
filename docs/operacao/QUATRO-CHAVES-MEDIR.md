# QUATRO-CHAVES-MEDIR — quantas notícias têm as quatro chaves, e o que a Intelligence pode cruzar

> Ramo `quatro-chaves-v2` (contém o vivo `83de0ccd`). **NÃO instalado.** Missão:
> `auditoria-madrugada/missao-quatro-chaves-medir.txt` (INT-LAW-091: sem chave não há cruzamento).
> Tudo em SÓ LEITURA: Sala real com `default_transaction_read_only=on`, armazém e livro só lidos,
> sem rede (proxy `127.0.0.1:9`), nenhum Postgres ligado. Trava D33 intacta: nada foi cruzado.

## Resposta curta

| | Itens | Cultura | Região do fato | Fase da planta | Período (JANELA) |
|---|---|---|---|---|---|
| **Sala — o que está GUARDADO hoje na coluna `janela_declarada`** | 94 | 0 | 0 | 0 | 0 |
| **Sala — o que o dono daria hoje, relendo pela estrada da produção** | 94 | 0 | 19 | 0 | 0 |
| **Acervo fora da Sala — o mesmo** | 1.158 | 4 | 51 | 0 | 0 |

- Todas as 94 linhas da Sala têm a janela no default «não medido» (94/94): pousaram antes da 033.
- **Período: 0 em 1.252.** Não é falta de dado — o dono escreve `NAO SEI` sempre, por lei
  (`admissao.janela_declarada`: «a régua não extrai intervalo nem safra; a janela é da CAP-WIN»),
  e a CAP-WIN é PROPOSTA/NOT_ACTIVE.
- **Cruzamentos cultura + região + período possíveis hoje: 0.** Sem o período, nenhum.

## 1. Conserto: `listar_pendentes` pelo nome

`admissao/sala_de_espera.py`: `listar_pendentes` lia `c[0]`, `c[1]`, `c[2]`. Agora o `select` nasce de
`COLUNAS_PENDENTES` (coluna → chave), cada valor casa com o seu nome, e um número de valores
errado rebenta (`SalaIndisponivel`) em vez de ler torto.

| Prova | Resultado | Ficheiro |
|---|---|---|
| 3 testes novos (`OsPendentesSaoPeloNome`) contra o código ANTIGO | 1 FAIL + 2 ERROR | `data/derivados/QUATRO-CHAVES-MEDIR/testes-pendentes-ANTES.txt` |
| `tests.test_sala_por_nome` inteiro DEPOIS | 9/9 OK | `…/testes-por-nome-DEPOIS.txt` |
| Mutação (M6 ordem↔item trocados na tabela · M7 sem conferir contagem · M8 volta o código posicional) | 3 mutantes, 3 mortos, ficheiro reposto nos 3 | `…/mutacao.py.txt`, `…/mutacao-RESULTADO.txt` |

Commits `526e5d92` (conserto + testes) e `307d5caa` (mutação).

⚠️ Ainda há, no mesmo ficheiro, duas leituras com **duas listas paralelas** (nomes num tuplo, colunas
no texto do SQL) casadas por `zip`: `ler_atual` e `linhas_para_revisao`. Não leem por número, mas
um desalinhamento entre as duas listas não rebenta (o `zip` corta calado). Fora do pedido; anotado.

## 2. A medida

### Como se mediu

`data/derivados/QUATRO-CHAVES-MEDIR/medir.py.txt` → `MEDIDA.json` (e `medir-SAIDA.txt`).
Para cada documento, a **mesma estrada do reprocesso** (`admissao/reprocessar_tempo_lugar.py`):
`italy_executor.tempo_e_lugar` (livro do coletor + página guardada, só com o sha256 certo) →
`orquestrador.item_documental_para_a_porta` (o LUGAR-FATO lê o texto) → **a decisão real da porta**
(`admissao.decidir`, para ter a evidência da régua) → o dono das chaves (`admissao.janela_para_o_ready`).
Conta como **provada** uma chave com `VALOR` e `BASE` diferentes de `NAO SEI`.

- **Sala**: as 94 linhas pela vista `sala_de_espera_atual` (valores já revistos), com o texto inteiro.
- **Acervo**: os sha256 distintos de `raw_asset` que nenhuma linha da Sala usa — **1.246 − 88 = 1.158**
  (a Sala tem 94 linhas sobre 88 brutos distintos: 6 brutos estão lá duas vezes). O texto vem do
  derivado `TEXT_EXTRACTION`/`TRANSCRIPTION` registado, lido de `~/sintonia-sala-italia/armazem`.
- Livro: cópia `auditoria-madrugada/tempo-lugar/livro-vivo-copia.ndjson` — sha256 igual antes e depois.

⚠️ Erro meu, corrigido antes desta medida: a 1.ª corrida trocava as quebras de linha do texto da Sala
por espaços, e o LUGAR-FATO lê frases — a região dava 2 em vez de 19. Com o texto inteiro dá **19,
exatamente as linhas que o caderno de revisões já tem com `fact_location`** (reprocesso de 25/09
19:07–19:54). A concordância é a prova de que o medidor anda pela mesma estrada.

### Onde está o texto (acervo)

| | Documentos |
|---|---|
| Com texto lido | 812 |
| Sem derivado de texto no registo (172 JSON — API/social; 14 HTML; 1 PDF; 1 CSV) | 188 |
| **Derivado registado no banco, ficheiro AUSENTE nesta máquina** (133 HTML, 23 PDF, 1 áudio, 1 vídeo) | 158 |

Dos 1.058 `TEXT_EXTRACTION` registados, **189 ficheiros não estão** em `~/sintonia-sala-italia/armazem`
(procurei também no vivo, em `acervo-tempo-lugar-v1`, `C:/capa-v1` e `auditoria-madrugada`: não achei).
NÃO SEI porquê. Esses 158 documentos contam como NAO SEI nas quatro chaves.

### Por classe T*

A régua de cultura existe **só para T1** (`CULTURA_OBRIGATORIA = {"T1": …}`), e a FASE são os
«momentos» que essa régua guarda **no SIM**. Fora de T1, cultura e fase são NAO SEI por construção —
mesmo quando o texto diz «fragole» ou «mele».

| Classe | Sala: itens · cult · região · fase · período | Acervo: itens · cult · região · fase · período |
|---|---|---|
| T1 | — (a Sala não tem nenhum T1) | 34 · 4 · 5 · 0 · 0 |
| T2 | 1 · 0 · 0 · 0 · 0 | 133 · 0 · 16 · 0 · 0 |
| T3 | 5 · 0 · 1 · 0 · 0 | 22 · 0 · 0 · 0 · 0 |
| T4 | — | 1 · 0 · 0 · 0 · 0 |
| T5 | 51 · 0 · 9 · 0 · 0 | 164 · 0 · 1 · 0 · 0 |
| T7 | 7 · 0 · 0 · 0 · 0 | 417 · 0 · 14 · 0 · 0 |
| T8 | — | 50 · 0 · 1 · 0 · 0 |
| T9 | 7 · 0 · 3 · 0 · 0 | 52 · 0 · 2 · 0 · 0 |
| T10 | 23 · 0 · 6 · 0 · 0 | 118 · 0 · 9 · 0 · 0 |
| T11 | — | 31 · 0 · 1 · 0 · 0 |
| T12 | — | 136 · 0 · 2 · 0 · 0 |

As 4 culturas do acervo são **2 documentos T1, cada um em 2 versões** (IT-T1-021: grano, patate ·
IT-T1-022: olivo, olive). Nenhum T1 do acervo teve SIM na porta hoje (14 NAO, 16 `NAO SEI`, 4 `NAO_SEI`)
— por isso a FASE fica 0 também em T1.

### Por fonte

A tabela completa, fonte a fonte e com as quatro chaves, está em `MEDIDA.json` (`CONTAS.*.POR_SOURCE_ID`).
Aqui, só as fontes com alguma chave provada:

**SALA** — 43 fontes; 9 com alguma chave provada (as outras 34: as quatro em NAO SEI em todos os itens)

| Fonte | Itens | Cultura | Região do fato | Fase | Período (JANELA) |
|---|---|---|---|---|---|
| IT-T10-018 | 23 | 0 | 6 | 0 | 0 |
| IT-T9-021 | 3 | 0 | 3 | 0 | 0 |
| IT-T5-015 | 2 | 0 | 2 | 0 | 0 |
| IT-T5-030 | 2 | 0 | 2 | 0 | 0 |
| IT-T5-186 | 2 | 0 | 2 | 0 | 0 |
| IT-T3-008 | 2 | 0 | 1 | 0 | 0 |
| IT-T5-010 | 1 | 0 | 1 | 0 | 0 |
| IT-T5-090 | 1 | 0 | 1 | 0 | 0 |
| IT-T5-160 | 3 | 0 | 1 | 0 | 0 |

**ACERVO** — 181 fontes; 32 com alguma chave provada (as outras 149: as quatro em NAO SEI em todos os itens)

| Fonte | Itens | Cultura | Região do fato | Fase | Período (JANELA) |
|---|---|---|---|---|---|
| IT-T2-025 | 14 | 0 | 6 | 0 | 0 |
| IT-T10-018 | 37 | 0 | 3 | 0 | 0 |
| IT-T2-034 | 9 | 0 | 3 | 0 | 0 |
| IT-T7-017 | 74 | 0 | 3 | 0 | 0 |
| IT-T7-042 | 27 | 0 | 3 | 0 | 0 |
| IT-T1-021 | 2 | 2 | 2 | 0 | 0 |
| IT-T10-013 | 2 | 0 | 2 | 0 | 0 |
| IT-T10-017 | 15 | 0 | 2 | 0 | 0 |
| IT-T2-008 | 2 | 0 | 2 | 0 | 0 |
| IT-T2-051 | 9 | 0 | 2 | 0 | 0 |
| IT-T7-125 | 3 | 0 | 2 | 0 | 0 |
| IT-T9-009 | 4 | 0 | 2 | 0 | 0 |
| IT-T1-009 | 1 | 0 | 1 | 0 | 0 |
| IT-T1-010 | 1 | 0 | 1 | 0 | 0 |
| IT-T1-018 | 1 | 0 | 1 | 0 | 0 |
| IT-T10-012 | 1 | 0 | 1 | 0 | 0 |
| IT-T10-021 | 7 | 0 | 1 | 0 | 0 |
| IT-T11-005 | 1 | 0 | 1 | 0 | 0 |
| IT-T12-014 | 15 | 0 | 1 | 0 | 0 |
| IT-T12-016 | 15 | 0 | 1 | 0 | 0 |
| IT-T2-014 | 1 | 0 | 1 | 0 | 0 |
| IT-T2-026 | 15 | 0 | 1 | 0 | 0 |
| IT-T2-032 | 5 | 0 | 1 | 0 | 0 |
| IT-T5-186 | 1 | 0 | 1 | 0 | 0 |
| IT-T7-019 | 3 | 0 | 1 | 0 | 0 |
| IT-T7-031 | 1 | 0 | 1 | 0 | 0 |
| IT-T7-043 | 3 | 0 | 1 | 0 | 0 |
| IT-T7-049 | 3 | 0 | 1 | 0 | 0 |
| IT-T7-112 | 2 | 0 | 1 | 0 | 0 |
| IT-T7-118 | 2 | 0 | 1 | 0 | 0 |
| IT-T8-005 | 15 | 0 | 1 | 0 | 0 |
| IT-T1-022 | 2 | 2 | 0 | 0 | 0 |

### 20 lidos à mão

Escolha: 12 ao acaso entre os itens com alguma chave provada + 8 ao acaso entre os itens com texto
e nenhuma chave (semente `20260926`; lista, trecho e valores em `MEDIDA.json` → `AMOSTRA_20`).
Li a frase que sustenta a região (a `BASE`) e, quando cortada, o texto inteiro.

| # | Fonte | Região dada | Região: certo? | Cultura: o texto tem? |
|---|---|---|---|---|
| 1 | IT-T10-018 | Firenze (lojas visitadas em Firenze) | CERTO | FALTOU: «mirtilli» (T10 não tem régua) |
| 2 | IT-T5-030 | Teramo (seminário na Univ. de Teramo) | CERTO (tema não agrícola) | não |
| 3 | IT-T5-015 | Napoli (workshop no CNR de Napoli) | CERTO | não |
| 4 | IT-T7-031 | Bologna | **ERRADO** — «Bologna Fiere, socio di FederBio»: nome de empresa | não |
| 5 | IT-T7-118 | Salerno (fórum em Salerno) | CERTO | não |
| 6 | IT-T2-025 | Lazio | **ERRADO** — «ARPA Lazio – Seminario»: nome da instituição que publica | não |
| 7 | IT-T5-015 | Napoli (o mesmo documento do #3, outra linha da Sala) | CERTO | não |
| 8 | IT-T5-186 | Brindisi ; Roma | **ERRADO** — página de lista: dois eventos diferentes colados numa só região | não |
| 9 | IT-T10-018 | Bolzano (Interpoma, Fiera Bolzano) | CERTO | FALTOU: «mela/meleto» |
| 10 | IT-T10-017 | Milano (Mercato Ortofrutticolo di Milano) | CERTO | FALTOU: «fragole» |
| 11 | IT-T2-026 | Genova (30 anos da Arpal em Genova) | CERTO | não |
| 12 | IT-T5-186 | Napoli («si terrà a Napoli il 28 settembre») | CERTO | não |
| 13 | IT-T7-020 | NAO SEI | certo (cita a ligação Panperduto–Malpensa, um percurso, não o lugar do fato) | não |
| 14 | IT-T12-007 | NAO SEI | certo | não |
| 15 | IT-T9-017 | NAO SEI | certo | FALTOU: «mora» |
| 16 | IT-T7-021 | NAO SEI | certo | não |
| 17 | IT-T7-035 | NAO SEI | certo | não |
| 18 | IT-T12-012 | NAO SEI | certo («Finestra sul Piemonte» é nome de programa) | não |
| 19 | IT-T10-018 | NAO SEI | certo | não |
| 20 | IT-T3-015 | NAO SEI | certo (página de contatos PEC) | não |

- **Região: 9 certas e 3 erradas em 12 valores dados; 8 NAO SEI justos em 8.** Os três erros têm
  forma: nome de empresa, nome da instituição que publica, página de lista com dois factos.
  Com 12 casos, a margem é larga: não é uma taxa, é um sinal.
- **Cultura: 0 valores dados nos 20; em 4 o texto nomeia a cultura** — lacuna da régua (só T1), não
  valor errado.
- Fase e período: NAO SEI nos 20; nenhum dos 20 declara uma fase da planta com clareza.

## 3. Cruzamentos que a Intelligence poderia tentar (NÃO executados)

| Chave do cruzamento | Grupos | Pares | Nota |
|---|---|---|---|
| cultura + região + período | **0** | **0** | período é NAO SEI em 1.252 de 1.252 |
| cultura + região (sem período) | 2 | 2 | os 2 são o **mesmo** boletim IT-T1-021 (grano/patate × Basilicata) em duas versões — não é cruzamento entre factos |
| só região (não é cruzamento pela INT-LAW-091; só para dimensionar) | 21 lugares com ≥ 2 documentos | 87 | 15 desses lugares têm ≥ 2 fontes diferentes (ex.: Milano 6 docs/5 fontes, Lazio 7/2, Abruzzo 5/3) — e 3 em 12 regiões da amostra estavam erradas |

**Com o que existe, a Intelligence não tem nenhum par legítimo para cruzar.** O que falta, por ordem de
peso: (1) um dono do **período** (CAP-WIN); (2) **cultura fora de T1** (o texto tem-na — 4 em 20 na
amostra); (3) a região sem os três erros de forma vistos acima.

## 4. Plano de reprocesso das linhas antigas pelo caderno de revisões (NÃO executado)

**Onde.** `janela_declarada` já é campo revisível (`CAMPOS_REVISIVEIS`, migration 033):
`sala_de_espera.rever()` escreve em `sala_de_espera_revisao`, a vista `sala_de_espera_atual` mostra a
última revisão. O RAW não muda, a linha não muda, nada se apaga; o mesmo código duas vezes não escreve
nada (compara valor e base atuais).

**O que falta no código** (a fazer em ramo próprio, com teste e mutação — não feito aqui):

1. `admissao/reprocessar_tempo_lugar.py` **não revê `janela_declarada`** (`revisoes_de` só leva
   `REVISTOS` + completude + evidência). Acrescentar a revisão da janela:
   `{"CAMPO": "janela_declarada", "VALOR": json.dumps(ready["JANELA_DECLARADA"], sort_keys=True,
   ensure_ascii=False), "BASE": "admissao.janela_para_o_ready sobre a linha revista (D58)"}`.
2. ⚠️ `ready_de` monta uma `Decisao` **sem evidência** («a linha já foi admitida: a decisão não se
   refaz»). O dono das chaves lê a cultura e a fase **da evidência da régua** — com essa Decisao dariam
   sempre NAO SEI. Para a janela: correr `admissao.decidir(item, universo)` **só para ler a evidência**,
   sem mudar a admissão da linha, e declarar isso no `MOTIVO` (e o resultado de hoje, se diferir).
3. `versao_do_codigo()` já assina `admissao/admissao.py`; confirmar que cobre `leis/fato_do_texto.py`
   e a régua (cobre, pela lista `CODIGO_DA_VERSAO`).

**Roteiro para o coordenador** (depois do código acima instalado):

1. Backup da Sala (o mesmo `pg_dump` dos backups diários) e robô parado.
2. Ensaio num Postgres descartável restaurado desse backup, com LOCK-PESADO:
   `py admissao/reprocessar_tempo_lugar.py --livros "<livro>" --raizes "~/sintonia-sala-italia/armazem" --saida recibo-seco.json`
   (sem `--aplicar`). **Esperado por esta medida: REGIÃO em 19 de 94; cultura, fase e período em 0.**
   Divergência = parar.
3. Aplicar no descartável (`--aplicar`), reler pela vista: 19 linhas com REGIAO_DO_FATO; 75 em NAO SEI.
   Correr outra vez: `INSERIDAS = 0`.
4. Só então na Sala real, com a mesma ordem.
5. **Desfazer**: nunca apagar revisões. Uma revisão nova com o default `JANELA_NAO_MEDIDA` (o mesmo
   `rever()`) faz a vista voltar a «não medido», com o porquê.

**Antes de aplicar, decidir** (é do dono, não meu): as 19 regiões levam para a chave os erros de forma
vistos na amostra (3 em 12). Aplicar já, com a base honesta, ou consertar primeiro o LUGAR-FATO
(nome de empresa/instituição, página de lista)?

**O acervo (1.158)** não tem linha na Sala: não há nada a rever. Entra pela missão ACERVO-PARA-SALA;
quem pousar com o código de `quatro-chaves-v2` já leva a janela preenchida pelo dono.

## Ficheiros (todos no ramo)

| Ficheiro | O quê |
|---|---|
| `data/derivados/QUATRO-CHAVES-MEDIR/ler_sala.py.txt` | leitor só-leitura da Sala (DSN do ficheiro, nunca impresso; recusa SQL que não seja `select`/`with`) |
| `data/derivados/QUATRO-CHAVES-MEDIR/medir.py.txt` | o medidor |
| `data/derivados/QUATRO-CHAVES-MEDIR/MEDIDA.json` | todas as contas, por item (sem texto), por fonte, por classe; a amostra dos 20 com trecho de 220 letras |
| `data/derivados/QUATRO-CHAVES-MEDIR/medir-SAIDA.txt` | a saída da corrida |
| `data/derivados/QUATRO-CHAVES-MEDIR/testes-*.txt`, `mutacao*` | o conserto do `listar_pendentes` |

Mapa: não regerado (PRONTO-SEM-MAPA; a INTEGRA-NOITE regera).
