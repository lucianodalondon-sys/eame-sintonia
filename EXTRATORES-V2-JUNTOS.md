# EXTRATORES-V2-JUNTOS — os dois extratores num ramo só, medidos numa cópia da Sala

Missão REPROC-EXTRATORES (coordenação 26/09, 10:30). Ramo `extratores-v2-juntos`: `extrator-evento-v2 @ 6971ddb1`
+ junção de `extrator-lugar-v2 @ 3b7c86da` (base comum dos dois: `91ab4eb3`, que já descende do vivo `69b0e23f`).
**Sem mapa** (PRONTO-SEM-MAPA). Sem rede. Sala real só LIDA (um `pg_dump` com `default_transaction_read_only=on`);
tudo o que escreve foi na **cópia** descartável. Nada instalado.

## 1. A junção
Um só conflito, em `leis/fato_do_texto.py`: **as duas missões consertaram o mesmo buraco** (o título curto
de um vídeo era deitado fora pela regra das 8 palavras), cada uma à sua maneira.

| ficou | de onde | porquê |
|---|---|---|
| a 1.ª linha do texto (o `<title>`) entra sempre, sem o nome do sítio; **fica** o pedaço depois do traço se tiver algarismos («… - 26 Maggio 2026») | LUGAR-V2 | já lida à mão 20/20; a regra da EVENTO-V2 cortava a data depois do traço |
| título e **descrição** do vídeo (`campos_do_fato(titulo=, descricao=)`) e, sem nenhuma frase longa, até 2 linhas curtas como título | EVENTO-V2 | a LUGAR-V2 não os tinha |
| `titulo_limpo` (título/descrição do vídeo) passa a usar **a regra da LUGAR-V2** | junção | antes cortava «- 12 giugno 2026» como se fosse nome do sítio |

Testes que mudaram por causa da junção (contrato, não erro): 1 da EVENTO-V2 (uma linha de menu na 1.ª linha
agora entra como título — o teste passou a pôr «Home» antes); 1 da D84 (ver 2). A ferramenta de mutação da
LUGAR-V2 (`ferramentas/lugar_v2/mutar_lugar_v2.py`) teve de apontar o M6 para a linha juntada.

## 2. «afide/afidi» contado em dobro — corrigido
`leis/boletim_do_campo.py`: lista declarada **`MESMO_PROBLEMA`** — o mesmo problema escrito de duas maneiras conta
**uma** vez; a forma do texto fica guardada em `FORMA` (e a porta leva-a em `PROBLEMA.SECOES`).
- singular/plural: afide/afidi, cimice/cimici, tripide/tripidi, psilla/psille, ruggine/ruggini, peronospora/e,
  nottua/e, nematode/i, batteriosi, pidocchio/i, tignola/e, tignoletta/e, **cocciniglia/e** (o plural «cocciniglie»
  nem era lido), dorifora/e, piralide/i;
- o nome científico entre parênteses a seguir ao comum: Halyomorpha halys = cimice asiatica, Bactrocera oleae =
  mosca dell'olivo, Lobesia botrana = tignoletta della vite, Ceratitis capitata / mosca mediterranea = mosca della
  frutta, Xylella fastidiosa = xylella;
- os dois nomes da mesma doença: mal bianco = oidio, muffa grigia = botrite, cercospora = cercosporiosi (medido
  aqui: o IT-T3-008 escreve as duas).
- De bónus, lido no IT-T3-010: «MOSCA DELLE OLIVE» era lida como **cabeçalho do olivo** e a praga perdia-se;
  agora é praga (e vai para o olivo pela regra da praga com a cultura no nome).

**Não é EPPO.** O que não está na lista fica como o texto escreve. Continua separado, por decisão: «cimice»
(genérico) ≠ «cimice asiatica»; «tignoletta» (sozinha) ≠ «tignoletta della vite»; «tignola» ≠ «tignoletta».

Efeito medido nos boletins da Sala (nomes distintos de praga): IT-T3-002 **25 → 22**, IT-T3-008 **25 → 18** e
**24 → 17**, IT-T3-010 6 → 6.

## 3. A cópia da Sala
`copia_sala.py.txt`: `pg_dump` só-leitura da Sala real → PostgreSQL descartável em `127.0.0.1:54391`
(`sala_copia_reproc`). Conferida: real e cópia com **94 / 94 / 1.562 / 1.063** (linhas / vista atual / brutos /
derivados); dump `bd6405d6…`, 2,7 MB. Desligada e apagada no fim (secção 7).

## 4. Antes → depois
Mesma cópia, mesmo livro, mesmo armazém; **só muda o código** (`medir.py.txt` com `CODIGO=<versão>`, a estrada do
reprocesso). Registo: `data/derivados/EXTRATORES-V2-JUNTOS/ANTES-DEPOIS.txt` e `MEDIDA-<versão>.json`.

Versões: **base** = `91ab4eb3` (antes dos dois extratores) · **EVENTO** = `6971ddb1` · **LUGAR** = `3b7c86da` ·
**JUNTOS** = `80ce1a3f` (este ramo; o código final não muda depois disto, só registos).

### 4a. Os 94 itens da Sala
| | a Sala guarda hoje | base | EVENTO | LUGAR | **JUNTOS** |
|---|---|---|---|---|---|
| data do fato (FACT_TIME) | 22 | 21 | 23 | 21 | **23** |
| lugar do fato (FACT_LOCATION) | 19 | 18 | 18 | 18 | **18** |
| cultura | 0 | 14 | 19 | 14 | **19** |
| praga/doença | 0 | 0 | 5 | 0 | **5** |
| fase | 0 | 0 | 6 | 0 | **6** |
| região do fato | 0 | 18 | 18 | 18 | **18** |
| período (janela) | 0 | 18 | 20 | 18 | **20** |
| **as 4 chaves juntas** (cultura+região+fase+período) | 0 | 0 | 1 | 0 | **1** |
| cultura + praga + data + lugar | 0 | 0 | 1 | 0 | **1** |

O único item com tudo junto é o boletim da ARIF Puglia (IT-T3-008 `85cb86eb`): olivo e vite · Puglia ; Lecce ·
2026-09-16/2026-09-22 · 17 pragas/doenças · fases por cultura.

### 4b. Os boletins
| | base | EVENTO | LUGAR | **JUNTOS** |
|---|---|---|---|---|
| **Sala, 5 T3 + 1 T2** — data / lugar / cultura / praga / fase / 4 chaves | 1 / 1 / 1 / 0 / 0 / 0 | 3 / 1 / 6 / 5 / 6 / 1 | 1 / 1 / 1 / 0 / 0 / 0 | **3 / 1 / 6 / 5 / 6 / 1** |
| **acervo, 124 boletins T2/T3 com texto** — data / lugar / cultura / praga / fase / 4 chaves | 14 / 10 / 0 / 0 / 0 / 0 | 27 / 18 / 1 / 3 / 8 / 0 | 14 / 10 / 0 / 0 / 0 / 0 | **27 / 18 / 1 / 3 / 8 / 0** |

### 4c. Tudo (94 + 1.158 do acervo = 1.252)
| | base | EVENTO | LUGAR | **JUNTOS** |
|---|---|---|---|---|
| data do fato | 57 | 106 | 61 | **106** |
| lugar do fato | 62 | 90 | 62 | **91** |
| cultura | 70 | 76 | 70 | **77** |
| praga | 0 | 8 | 0 | **8** |
| fase | 0 | 14 | 0 | **14** |
| período | 36 | 79 | 39 | **79** |
| 4 chaves juntas | 0 | 1 | 0 | **1** |

Base → JUNTOS, item a item: data do fato **+49, 0 perdidas, 0 trocadas**; lugar do fato **+30, 1 perdido,
3 trocados**. O perdido foi lido: IT-T8-005 (vídeo «Agriumbria 2026 presentata alla Fiera del Levante di Bari»)
— a descrição diz que a feira é **em Bastia Umbra, 27-29 marzo 2026**, e Bari foi só onde foi apresentada. Tirar
Bari está certo; pôr Bastia Umbra é do leitor de lugar (comune sem a lista ISTAT, ver limites).

**O que os dois juntos dão a mais do que cada um:** quase tudo vem da EVENTO-V2; a LUGAR-V2 sozinha dá +4 datas
e +3 períodos, que a EVENTO-V2 já apanhava pelo título. Juntos: +1 lugar e +1 cultura em relação à EVENTO-V2.

### 4d. Pares que a Intelligence consegue cruzar
Par = dois **documentos diferentes** (sha256 do bruto) com a mesma cultura, a mesma região e período sobreposto.
| | base | EVENTO | LUGAR | **JUNTOS** |
|---|---|---|---|---|
| documentos com cultura + região + período | 6 | 7 | 6 | **7** |
| pares | 2 | 2 | 2 | **2** |
| … entre fontes diferentes | 0 | 0 | 0 | **0** |
| … com a mesma praga | 0 | 0 | 0 | **0** |

**Os extratores não criaram nenhum par novo.** Os 2 pares que existem são a mesma fonte duas vezes
(IT-T1-021 grano/patate Basilicata; IT-T9-009 pomodoro Piacenza) — não são duas provas independentes. O 7.º
documento novo (o ARIF) não tem par: nenhum outro documento fala de olivo/vite na Puglia na mesma semana.

## 5. O reprocesso aplicado — na cópia
`admissao/reprocessar_tempo_lugar.py --aplicar` com o código JUNTOS, contra a **cópia**: 94 linhas, 299 revisões
novas, 359 já eram assim (append-only, a linha não muda). Depois, lido pela vista que a Intelligence lê
(`ler_vista.py.txt` → `VISTA-DEPOIS-DO-REPROCESSO.json`):

| vista `sala_de_espera_atual`, 94 itens | antes | depois |
|---|---|---|
| data do fato | 22 | **23** (o ARIF ganhou a semana do cabeçalho) |
| lugar do fato | 19 | **18** |
| cultura / região / fase / período | 0 / 0 / 0 / 0 | **19 / 18 / 6 / 20** |
| praga | 0 | **5** |
| 4 chaves juntas | 0 | **1** |
| pares (mesma cultura + região + período) | 0 | **0** |

O lugar que se perde (IT-T5-186, página de ENEA com vários eventos, guardado «Brindisi ; Roma») **não é destes
extratores**: já sai NAO SEI na base `91ab4eb3`, pela regra da CONSERTO-REGUA (numa lista de eventos, o lugar de
outro evento não é o deste). Declaro-o porque a Sala real perderia esse lugar quando o reprocesso correr lá.

## 6. Testes e mutação (rede fechada)
- Baterias dos dois: `test_extrator_evento_v2`, `test_boletim_do_campo`, `test_extrator_lugar_v2`,
  `test_fato_do_texto` — **121 passam**. Novos nesta missão: 6 (MESMO_PROBLEMA, mosca delle olive, linha que segue
  a cultura) + 3 (título da junção) + asserções da FORMA na porta.
- Mutação da EVENTO-V2 + junção: **49/49** (`mutacao.py.txt`; a 1.ª volta deu 42/47 — os 5 sobreviventes eram
  buracos de teste; um deles achou o plural «cocciniglie» que não era lido).
- Mutação da LUGAR-V2 sobre o código junto: **8/8**.
- Regressão: os **100 ficheiros de teste** que importam o que mudou (leitor do fato e do lugar, boletim, porta,
  Sala, reprocesso, orquestrador, YouTube), cada versão numa cópia própria, rede fechada, comparados **pelo nome**:
  base `91ab4eb3` **2.452 testes, 165 falhas/erros** (97 ficheiros; 3 são novos) · JUNTOS `80ce1a3f` **2.529 testes
  (+77), as MESMAS 165 falhas/erros, nenhuma nova e nenhuma a menos** (`regressao-BASE-nomes.txt`,
  `regressao-RAMO-nomes.txt`). As 165 são as falhas de base desta máquina (ver a suíte que já chega vermelha).

## 7. Limpeza
- Cópia da Sala desligada e a pasta apagada (`COPIA-DESLIGADA.json`); porta 54391 sem ninguém a escutar.
- As 5 cópias de código de medida (`C:/nuvem/medir-reproc/*`) removidas com `git worktree remove`.
  ⚠️ Erro meu, desfeito: um primeiro `git worktree add /c/nuvem/…` criou 4 cópias em `C:/c/nuvem/…` (o git nativo
  leu `/c/` como pasta). Removidas com `git worktree remove`; `C:/c/Users` (que não é desta missão) intacta.
- `LOCK-PESADO.txt` libertado (vazio).

## 8. Limites declarados
- **Mapa por correr** (PRONTO-SEM-MAPA): `leis/boletim_do_campo.py` continua sem peça (P9), como na EVENTO-V2.
- `MESMO_PROBLEMA` é uma lista curta e declarada, não EPPO; nomes fora dela continuam a contar como o texto
  escreve (ex.: «cimice» genérico e «cimice asiatica» continuam dois).
- 0 pares entre fontes diferentes: o gargalo já não é o leitor — é haver **duas fontes** sobre a mesma
  cultura, região e semana. Isso é coleta, não extração.
- Bastia Umbra (IT-T8-005) e outros comuni: sem a lista ISTAT declarada, o leitor de lugar não os conhece
  (a LUGAR-V2 já o disse: 0 de 969 pela sigla).
- As decisões pendentes da EVENTO-V2 continuam do dono: o período do cabeçalho como `fact_time`; colunas próprias
  para praga/fase na Sala.
- A Sala real **não** foi reprocessada — só a cópia. Instalar e reprocessar é do coordenador.

## EM PALAVRAS SIMPLES
- **Juntei as duas missões num lugar só.** A do "quando aconteceu" e a do "onde aconteceu" tinham consertado
  o mesmo buraco (o título curto dos vídeos), cada uma do seu jeito. Fiquei com o melhor das duas. O que muda
  para você: os dois consertos agora andam juntos e podem ser instalados de uma vez.
- **O "afide/afidi" não conta mais dobrado.** É como contar "pulgão" e "pulgões" como duas pragas. Agora é uma
  só. O mesmo vale para o nome científico entre parênteses: "cimice asiatica (Halyomorpha halys)" é um bicho só.
  No boletim de Salerno, a lista caiu de 25 nomes para 22; num boletim da Puglia, de 25 para 18. Achei ainda
  duas coisas no caminho: a palavra "cocciniglie" (plural) nem era lida, e "MOSCA DELLE OLIVE" era lida como se
  fosse o título da seção do olival, e a praga sumia.
- **Medi numa cópia da Sala, não na Sala de verdade.** É como fazer uma fotocópia do caderno e rabiscar
  na fotocópia. A cópia era igual à original (94 itens) e já foi desligada e apagada. A Sala real só foi lida.
- **O que ganhou** (94 itens da Sala + 1.158 do acervo = 1.252):
  - data do acontecimento: de 57 para 106. Nenhuma data que já existia se perdeu.
  - lugar do acontecimento: de 62 para 91. Só um se perdeu, e com razão: um vídeo dizia "Bari", mas a feira é
    em Bastia Umbra; Bari foi só onde ela foi apresentada.
  - praga: de 0 para 8. Fase da planta: de 0 para 14.
  - as 4 chaves juntas (cultura + região + fase + período): de 0 para 1 em 1.252. É o boletim da Puglia
    (oliveira e videira, Lecce, semana de 16 a 22 de setembro, 17 pragas).
- **O que NÃO ganhou: pares para a Intelligence cruzar.** Continuam 2, e os dois são a mesma fonte repetida.
  Entre fontes diferentes: 0 antes, 0 depois. É como ter só um jornal: não dá para confirmar a notícia com
  um segundo. O leitor já não é o problema. O que falta é coletar uma segunda fonte que fale da mesma cultura,
  na mesma região, na mesma semana.
- **Nada quebrou.** A sabotagem proposital foi pega 49 de 49 vezes (e 8 de 8 na parte do lugar). A bateria de
  100 arquivos de teste deu as mesmas 165 falhas de antes, que já existiam, e nenhuma nova.
- **Uma coisa pode surpreender quando a Sala real for reprocessada:** uma página da ENEA perde o lugar
  "Brindisi ; Roma". Não é destes extratores. É uma regra de outra missão (CONSERTO-REGUA), que já está na
  base: numa lista de vários eventos, o lugar de um evento não vale para o outro.
- **Falta:** o mapa do sistema (por isso é "sem mapa"). Instalar e reprocessar a Sala real é do coordenador.
