# RELATÓRIO · LUGAR-E-TEMPO-DO-FATO (D61 + D62 + D63 + D64 + DA-6 + DA-7) · ramo `lugar-fato-v1`

**DA-6:** o LUGAR-FATO é o **único** dono de `fact_time` / `fact_location` a partir do texto, incluindo as
relativas D63/D64; a nuvem tempo-publicacao fica só com PUBLICATION_TIME e SOURCE_LOCATION.

Missão: `fact_location` e `fact_time` **a partir do texto**, com evidência. Pelo ACRESCENTO da
coordenação, esta bancada faz **só o extrator** (função pura, com testes); a TEMPO-E-LUGAR faz o
encanamento de ponta a ponta e liga a função.

Base: produção `origin/servico-20260923-0923` (`df0865e6`). Rede fechada. O vivo e a Sala não foram
tocados — a Sala foi lida por um único `SELECT` só-leitura (78 linhas de `sala_de_espera`), guardado
**fora do Git** em `C:/Users/London1/lugar-fato/sala-78.json`.

Regras do dono aplicadas:
- **D62**: facto = o que muda no campo + eventos técnicos (feira, congresso, dia de campo) como tipo
  próprio + ecossistema do agronegócio. Nada é descartado por lhe faltar data ou lugar; regista-se o que
  há, com base e grau de precisão.
- **D63** (substitui o ponto 3 da D62): data relativa vale como `fact_time` **só** com a publicação
  provada e a conta feita; «ieri» = dia; «la settimana scorsa» = intervalo; sem publicação provada = NAO SEI;
  a precisão marca CALCULADA.
- **D64**: «oggi» só conta quando o texto deixa claro que é o próprio dia («oggi, lunedì», «oggi è
  stato», «oggi alle», «oggi 25 settembre»); «oggi» no sentido de «hoje em dia» («oggi i consumatori»,
  «ad oggi», «al giorno d'oggi») = NAO SEI.
- **Coordenação 25/09**: (a) onde se PLANTA/COLHE é CAMPO, mesmo numa notícia de mercado; (b) data de
  exame de faculdade é INSTITUCIONAL_NAO_FATO (o nome da REGUA-FATO); (c) a prova da publicação
  combinada com a TEMPO-E-LUGAR (secção 1).

## 1. A interface (o que a TEMPO-E-LUGAR liga)

```python
from leis.fato_do_texto import campos_do_fato      # ou sys.path + import fato_do_texto
r = campos_do_fato(texto, publication_time=None, publication_time_basis=None)
r["fact_location"]            # "NAO SEI"  ou  "Grosseto ; Siena"   (todos do MESMO tipo, " ; ")
r["fact_location_basis"]      # "CAMPO · OCORRENCIA · CITADO · PROVINCE · âncora «constatata» · CONFIRMED_FOCUS · «trecho»"
                              # "CAMPO · PRODUCAO · CITADO · REGION · âncora «si producono» · OTHER · «trecho»"  ou  "NAO SEI · porquê"
r["fact_location_kind"]       # CAMPO | EVENTO | MERCADO | NAO SEI
r["fact_location_precision"]  # COUNTRY | REGION | PROVINCE | NAO SEI
r["fact_time"]                # "NAO SEI" | "12 settembre" | "12-13 novembre 2026" | "2026-09-22" | "2026-09-14/2026-09-20"
r["fact_time_basis"]          # "CAMPO · AMARRADO_AO_ACONTECIMENTO · DATE_EXACT · «trecho»"
                              # "RELATIVA_A_PUBLICACAO"    (DA-7: calculada, e deu OUTRO dia que não o da publicação)
                              # "PUBLISHED_AT_COM_PROVA"   (DA-7: calculada, e deu o PRÓPRIO dia da publicação — «oggi, lunedì»)
                              # "NAO SEI · porquê (e as expressões relativas guardadas)"
r["fact_time_calculo"]        # "RELATIVA_A_PUBLICACAO" quando a data foi calculada; senão "NAO_SE_APLICA"
r["fact_time_evidencia"]      # quando calculada: "CAMPO · DATE_EXACT+CALCULADA · «ieri» contado a partir da publicação provada 2026-09-23 (…) · «trecho»"; senão "NAO_SE_APLICA"
r["fact_time_kind"]           # CAMPO | EVENTO | NAO SEI
r["fact_time_precision"]      # DATE_EXACT | WEEK | MONTH | SEASON | APPROXIMATE | NOT_KNOWN, com "+CALCULADA" quando veio da conta
r["EVIDENCIA"]                # LUGARES (todos, de todos os tipos, cada um com KIND, ESPECIE, PAPEL_NA_LEI e trecho),
                              # TEMPO, TEMPOS_DE_EVENTO, EXPRESSOES_RELATIVAS, PUBLICACAO_PROVADA (à parte), LINHAS_DE_CORPO
```

- `fact_location`, `fact_location_basis`, `fact_time` e `fact_time_basis` são as colunas da Sala e do
  tradutor da porta (`coleta/ingresso.py:314-331`). `_kind` e `_precision` **não têm coluna na Sala**:
  vão também escritos no início da `_basis`. Criar colunas é decisão da TEMPO-E-LUGAR e do dono.
- **Não recebe `SOURCE_LOCATION` nem a data de coleta.** Não há caminho para nenhum dos dois entrar.
- **(c) A prova da publicação, combinada com a TEMPO-E-LUGAR** (mensagem enviada a ela em 25/09):
  `publication_time` = o `PUBLISHED_AT` dela (data ISO); `publication_time_basis` = o `PUBLISHED_AT_BASIS`
  dela. Conta como provada só se vierem as duas, a data for ISO e a base não começar por
  `NAO SEI`/`NÃO SEI`/`UNKNOWN`. Serve para duas coisas: descartar a data do texto que é o carimbo da
  publicação, e fazer a conta das relativas. Sozinha nunca vira `fact_time`. ⚠️ A Sala hoje **não
  guarda a base**: chamar só com `published_at` = nenhuma relativa contada. `CAPTURED_AT` não entra.
- Ponto de ligação sugerido (achado da TEMPO-E-LUGAR, `ACHADO-TEMPO-E-LUGAR-0932.txt`):
  `orquestrador/orquestrador.py:572-577` ou `admissao/admissao.py:1893-1918`. O sítio é escolha dela.

## 2. O que a função faz

**Não há um segundo leitor de italiano para o CAMPO.** Quem lê é `leis/fato_local.py`, que veio da
Itália e diz «atualizar = repuxar da Itália, não editar aqui». **Não foi editado.** À volta dele:

1. **O corpo, não a página.** Linha com menos de 8 palavras (menu, título) ou com cara de rodapé
   (morada, CAP, tel, p.iva, cookie, registro stampa…) não alimenta nem lugar nem tempo.
2. **EVENTO e MERCADO como tipos (D62).** O leitor recusa de propósito o lugar de congresso/feira e o de
   mercado (falso positivo do Brasil: a feira virava «lugar da doença»). Aqui essa recusa vira **tipo**:
   - lugar recusado numa frase com palavra de evento → `EVENTO` (papel na lei: `EVENT`);
   - lugar recusado por «mercato» → `MERCADO` (papel na lei: `AREA_COMERCIAL`);
   - `TIPO_DE_EVIDENCIA` destes é sempre `OTHER`: **nunca** foco, observação ou amostra;
   - havendo lugar `CAMPO`, `fact_location` só tem `CAMPO`; os outros ficam na EVIDENCIA e na base
     («também citados, de outro tipo: Bologna (EVENTO)»);
   - o lugar só é promovido se estiver escrito com maiúscula («fermo» ≠ Fermo);
   - **(a) onde se planta/colhe é CAMPO** (`ESPECIE = PRODUCAO`, `TIPO_DE_EVIDENCIA = OTHER`: nunca foco
     de praga): a palavra de produção tem de estar a até 60 letras do lugar, e vence a âncora mais perto
     («del mercato In Sardegna si producono» → Sardegna = CAMPO). Só verbos de plantar/colher: `si
     producono`, `è/sono prodotto`, `coltivat*`, `coltivazion*`, `raccolto`, `vendemmia`, `piantat*`,
     `ettari`, `frutteti`, `vigneti`, `oliveti`, `agrumeti`. **Tirei**, depois de medir, `produzione`
     («produzione scientifica», «Istituto di Produzioni Vegetali»), `raccolta` (de textos), `colture`
     («protezione delle colture»), `campi` e `produttori` («i produttori di Firenze» = onde a entidade está);
   - a âncora mais perto decide também entre EVENTO, MERCADO e PRODUCAO;
   - «eventi estremi / meteorologici / atmosferici» não é evento técnico, é tempo no campo.
3. **Data de EVENTO.** Numa frase com palavra de evento: «12 e 13 novembre 2026», «dal 6 all'8 ottobre»,
   «16-24 maggio», «8 ottobre 2026». Intervalo → `APPROXIMATE` com o intervalo escrito; um dia → `DATE_EXACT`.
   Ordem: data explícita de CAMPO > relativa de CAMPO > data de EVENTO > relativa de EVENTO.
4. **Relativas (D63 + D64).** Com publicação provada, e só se a frase estiver presa a um facto (palavra
   de campo do leitor, com palavra inteira, ou palavra de evento), e não for frase institucional:

   | expressão | conta | precisão |
   |---|---|---|
   | **oggi com marca de dia** (D64): «oggi, lunedì», «oggi 25 settembre», «oggi alle», «oggi è stato», «oggi pomeriggio/mattina/sera», «nella giornata di oggi» | o dia da publicação | DATE_EXACT+CALCULADA |
   | **oggi sem marca**, «ad oggi», «fino ad oggi», «al giorno d'oggi» (D64) | **NAO SEI** — pode ser «hoje em dia» | — |
   | stamattina, stamane, stasera, stanotte | o dia da publicação | DATE_EXACT+CALCULADA |
   | ieri · l'altro ieri · domani · dopodomani | −1 · −2 · +1 · +2 dias | DATE_EXACT+CALCULADA |
   | lunedì scorso … domenica scorsa | o último desse dia **antes** da publicação | DATE_EXACT+CALCULADA |
   | la settimana scorsa / la scorsa settimana | **segunda a domingo** da semana anterior | WEEK+CALCULADA |
   | questa settimana · la prossima settimana | segunda a domingo da semana | WEEK+CALCULADA |
   | il mese scorso | 1.º ao último dia do mês anterior | MONTH+CALCULADA |
   | l'anno scorso | 1/1 a 31/12 do ano anterior | APPROXIMATE+CALCULADA |
   | nei giorni scorsi · di recente · recentemente | **sem medida**: fica como evidência, nunca vira data | — |

   Intervalo em ISO 8601 (`2026-09-14/2026-09-20`): **nunca um dia inventado dentro dele**. Sem
   publicação provada = `NAO SEI`, e a expressão fica na EVIDENCIA e na base. Mais três regras:
   - **termo de comparação não conta**: «rispetto allo stesso periodo dello scorso anno», «rispetto alla
     settimana scorsa» — o ano passado é a régua, não o tempo do facto (medido em IT-T3-008);
   - **duas contas diferentes no mesmo texto = NAO SEI (AMBIGUO)** — a mesma regra da nuvem tempo-publicacao;
   - cada expressão guarda na EVIDENCIA o porquê de não ter sido contada.
5. **O que não é tempo do facto é tapado**: série de anos, carimbo de lista no início da linha, prazo, e
   **(b) frase institucional** (esame, appello, colloquio, lezioni, laurea, corso di laurea, iscrizione,
   bando, concorso, tesi, tirocinio, graduatoria, CFU, didattica, dottorato) → `INSTITUCIONAL_NAO_FATO`.
6. **As âncoras do leitor só contam como palavra inteira.** O leitor italiano procura «coltura» sem
   fronteira: casa dentro de «agricoltura» e «arboricoltura». Por isso qualquer frase com «agricoltura»
   amarrava uma data. Aqui a data do leitor é conferida com a âncora a começar uma palavra; se não,
   é tapada nessa frase (`ANCORA_DENTRO_DE_OUTRA_PALAVRA`) e o leitor é perguntado de novo. Foi assim
   que «l'esame … di arboricoltura … il 21 settembre» e «Laurea … nel 2022» viraram data de CAMPO.

## 3. Lista de lugares: o que existe e o que falta

Não existe no repositório uma lista oficial de comuni. A que existe é o `GAZETTEER` de
`leis/fato_local.py`: **20 regiões + 85 províncias** (das 107) + o país. Não acrescentei lista
nenhuma: a regra é trazer da Itália. **O ramo da Itália (`claude/sintonia-italy-pilot-b1l401`) já não tem
`leis/fato_local.py`** (foi apagado lá), portanto hoje não há versão para puxar. Consequência:
comune nunca sai (o capoluogo sai como província), 22 províncias ficam invisíveis, e lugares fora da
Itália (Madrid) também.

## 4. A medida nas 78 da Sala (`scripts/lugar_fato/MEDIDA-LUGAR-TEMPO-78-V1.json`, DATASET V2)

| campo | saem de NAO SEI | por tipo | D63 (antes) | D61 |
|---|---|---|---|---|
| `fact_location` | **12 de 78** | CAMPO 3 (ocorrência 1 · produção 2) · EVENTO 6 · MERCADO 3 | 12 | 1 |
| `fact_time` | **18 de 78** | CAMPO 9 · EVENTO 9 | 20 | 13 |

**Relativas (D63/D64):** a Sala não guarda a base da publicação, por isso nenhuma é contada. Para saber
quanto a regra muda, simulei uma publicação «provada» inventada (só a contagem sai, nenhum valor):
**0 de 78** ganhariam data por conta. As que há são «oggi» sem marca de dia (13 linhas, recusadas pela
D64), «scorso anno» em comparação (IT-T3-008) ou «oggi 22 settembre», onde a data escrita já vence.
Ou seja: **nestas 78, a D63 não acrescenta nenhuma data**; ela vale para textos que ainda não temos.

### 4.1 Leitura à mão — li as 30 respostas (12 lugares + 18 datas)

**A classificação é minha, uma pessoa só, pelos trechos. Pode ter erro de um ou dois.**

**Lugar, 12 de 78:**
- **certos, 7**: IT-T3-008 Puglia (CAMPO/ocorrência) · IT-T10-018 **Sardegna (CAMPO/produção — era
  MERCADO, corrigido por (a))** · IT-T5-015 Napoli (EVENTO, 2 linhas) · IT-T10-018 Milano (MERCADO) ·
  IT-T10-018 Piemonte/Lombardia (MERCADO; aberturas de supermercado — lugar certo, tipo depende da
  fronteira GDO da REGUA-FATO) · IT-T5-090 Roma/Milano/Brescia/Padova/Napoli (EVENTO; congressos de
  demografia, não de agro).
- **meio certos, 3**: IT-T5-010 Ferrara (certo, «24mila ettari») + Italia (a mais) · IT-T10-018
  Sicilia/Verona (Verona é o mercado; a Sicília é onde a produção caiu — «riduzione della produzione»,
  e `produzione` saiu da lista, por isso a Sicília ficou MERCADO) · IT-T10-018 Rimini (certo) + Piemonte/Italia.
- **errados, 2**: IT-T5-033 «Italy» (2 linhas; o trecho não diz onde é o evento).

**Data, 18 de 78:**
- **certas, 13**: campagna 2010 · 12-13 novembre 2026 (×2) · **29 settembre 2026 (×2, agora EVENTO — era
  CAMPO)** · raccolta 2026 · stagione 2026 · 2025 (meta dos retalhistas) · 23 settembre 2026 · 2025
  (fundos do caranguejo-azul) · 6-8 ottobre 2026 · 20-22 aprile 2027 · maggio (pólen).
- **data certa, evento fora do agro, 3**: IT-T5-030 «8 ottobre 2026» (×2, seminário de cibercrime) ·
  IT-T5-090 «1-4 febbraio 2023» (congresso de demografia). O extrator diz EVENTO; é a REGUA-FATO
  (tipo do documento) quem diz que não é agro.
- **erradas, 2**: IT-T3-010 «luglio» (é conselho) · IT-T10-018 «2025» (ano de comparação de preço).

**O que saiu, e porquê (as correções desta volta):**
- IT-T5-049 «21 settembre» (exame adiado) → NAO SEI, `ANCORA_DENTRO_DE_OUTRA_PALAVRA` («arboricoltura»);
  e o «colloquio … si svolgerà il 23 settembre» também → `INSTITUCIONAL_NAO_FATO`.
- IT-T5-029 «2022» (início de um curso) → `INSTITUCIONAL_NAO_FATO`.
- Erro meu nesta volta, corrigido antes de entregar: a primeira lista de produção fazia **15** lugares
  CAMPO, a maioria errada («produzione scientifica», «Istituto di Produzioni Vegetali», «raccolta» de
  textos, «protezione delle colture»). Apertei a lista e pus a distância de 60 letras; ficaram 2, os dois
  certos. Dos 13 que saíram, 11 eram errados e 2 certos (Sicília e Emilia-Romagna) — perdi esses 2.

Resumo: lugar certo ou meio certo em **10 de 12**; data certa em **13 de 18**, mais 3 com a data
certa mas de um evento fora do agro; **2 de 18 erradas** (eram 4 de 20).

## 5. Testes e mutação

- `tests/test_fato_do_texto.py` — **37 testes, verdes** (33 + 4 da DA-7) (`py -m unittest tests.test_fato_do_texto`).
  Novos nesta volta: D64 (5 formas de «oggi» que são o dia, 5 que não são, «oggi» sem publicação),
  (a) produção numa notícia de mercado é CAMPO/OTHER, mercado perto continua MERCADO, produção longe
  (>60 letras) não conta, (b) exame adiado = INSTITUCIONAL_NAO_FATO, «agricoltura» não amarra data,
  termo de comparação, duas contas = AMBIGUO.
- `scripts/lugar_fato/mutar_fato_do_texto.py` → `MUTACAO-FATO-DO-TEXTO-V1.json`: **34 mutantes, 34 mortos** (31 + M28–M30 da DA-7).
  Só conta como morto se **um teste falhou** (asserção); erro de execução não conta.
  M1 source_location copiado · M2 publicação vira fact_time · M3 menu conta · M4 rodapé conta ·
  M5 relativa sem base da publicação · **M5b a conta usa a data de coleta (hoje) em vez da publicação** ·
  M5c a função aceita a data de coleta como reserva · M6 base NAO SEI ancora · M7/M7c/M7d cada proteção
  de tempo desligada · M8 só o primeiro lugar · M9 base sem trecho · M10 evento vira CAMPO · M11 mercado
  vira CAMPO · M12 evento passa à frente de CAMPO · M13 semana vira um dia · M14 «nei giorni scorsi» vira
  data · M15 precisão esconde CALCULADA · M16 «fermo» volta a ser Fermo · M17 «eventi estremi» vira evento ·
  **M18 «oggi» sem marca conta · M19 «ad oggi» conta · M20 «oggi, lunedì» deixa de contar** · M21 produção
  volta a MERCADO · M22 produção ganha evidência de foco · M23 exame volta a ser facto · M24 «coltura»
  dentro de «agricoltura» volta a amarrar · M25 duas contas escolhem uma · M26 comparação conta ·
  M27 produção longe do lugar conta.
- Errei duas vezes nas voltas anteriores, e corrigi: o primeiro M7 só mudava o **nome** da proteção; o
  primeiro M5 «morria» por **erro de execução**, não por um teste.

## 6. Q2 · palavras propostas para o leitor italiano (não aplicadas)

O ramo da Itália já não tem o leitor, por isso não há versão para puxar, e a lei do repo não deixa
editá-lo aqui. As palavras de EVENTO vivem em `leis/fato_do_texto.py` (`ANCORAS_DE_EVENTO`). As de CAMPO
e de agronegócio abaixo ficam **propostas** — hoje fazem falta nas 78:

- **tempo e clima que mudam o campo** (a CAMPO, lugar e data): `precipitazion[ei]`, `piogg[ei]a`,
  `sono cadut[ei]`, `grandinat[ae]`, `gelat[ae]`, `siccità`, `ondat[ae] di calore`, `temperature`,
  `eventi estremi`, `danni`, `allagament`, `esondazion`.
- **fenologia e produção**: `polline`, `picco pollinico`, `fioritura`, `invaiatura`, `vendemmia`,
  `semina`, `trebbiatura`, `produzione`, `resa`, `raccolt[oa]` (já existe).
- **preço e mercado medido**: `rilevazione`, `prezz[io]`, `quotazion[ei]`, `listino`.
- **ecossistema do agronegócio (D62)**: `molecola`, `principio attivo`, `registrazione`,
  `autorizzat[oa]`, `revoca`, `lancio`, `acquisizion[ei]`, `fusione`, `nuovo stabilimento`,
  `nuova apertura`.
- **regra, não palavra**: exigir maiúscula no topónimo (`mencoes()` compara em minúsculas; «fermo» casa
  com Fermo). Aqui já se exige para EVENTO/MERCADO; no leitor ficaria para todos.

## 6b. DA-7 · a data calculada passa na lei do artefato sem mexer na lei

`leis/artefato.py::conferir` (linha 352) reprova `FACT_TIME == PUBLISHED_AT`, a não ser que
`NOTES.FACT_TIME_BASIS` seja **exatamente** `PUBLISHED_AT_COM_PROVA`. Com a D64, «oggi, lunedì» dá o
próprio dia da publicação — e com a publicação só com o dia («2026-09-21») a lei reprovava (provado).
**A lei não foi tocada.** No extrator, quando a data é calculada:

| a conta deu… | `fact_time_basis` | `fact_time_calculo` | `fact_time_evidencia` |
|---|---|---|---|
| o dia da publicação («oggi, lunedì») | `PUBLISHED_AT_COM_PROVA` | `RELATIVA_A_PUBLICACAO` | expressão + conta + trecho |
| outro dia ou intervalo («ieri», «la settimana scorsa») | `RELATIVA_A_PUBLICACAO` | `RELATIVA_A_PUBLICACAO` | expressão + conta + trecho |
| data não calculada | a base descritiva de sempre | `NAO_SE_APLICA` | `NAO_SE_APLICA` |

Testes contra a lei verdadeira (`leis.artefato.conferir`): «oggi, lunedì» com publicação só-dia **passa**;
o mesmo com a base antiga **reprova** (prova de que o teste morde); «ieri» passa com
`RELATIVA_A_PUBLICACAO`. Mutantes: M28 tira a marca (morre), M29 põe a marca sempre (morre), M30 perde a
evidência da conta (morre). **37 testes; mutação 34/34.** A medida nas 78 saiu igual, byte a byte.

## 7. Coordenação com as outras bancadas

- **TEMPO-E-LUGAR** (sessão `tempo-lugar-v1-98`): mensagem enviada com a interface da secção 1 e o
  pedido de **juntar por merge** (o `tempo-lugar-v1` leva uma cópia antiga, `cf372dcb`, segundo o
  aviso do PACOTE-TEMPO-LUGAR). Ainda sem resposta — não sei se ela aceitou.
- **REGUA-FATO** (`regua-fato-v1`): não aparece na lista de sessões; deixei o bilhete
  `auditoria-madrugada/LUGAR-FATO-PARA-REGUA-FATO-1215.txt`. Ponto principal: o meu «kind» é **por
  campo** (lugar e data), o dela (`fact_kind`) é **do documento**; usei o nome dela
  `INSTITUCIONAL_NAO_FATO`; e avisei que o leitor italiano tem o buraco da âncora sem palavra inteira.
- **⚠️ A conta D63 existe duas vezes** (aviso do PACOTE): aqui e em
  `coleta/executor_texto_de_html.py::tempo_do_fato_relativo` (nuvem tempo-publicacao). As regras diferem:
  - esta só conta se a frase falar de um facto;
  - esta aplica a D64 e recusa o termo de comparação;
  - a da nuvem lê o texto inteiro, deixa «oggi» e «anno scorso» sempre de fora e aceita «N giorni fa»;
  - as duas recusam quando há duas contas diferentes;
  - a precisão escreve-se `DATE_EXACT+CALCULADA` (vocabulário da lei) contra `CALCULADA:DIA`.
  **Quem escolhe um dono único é o coordenador.** Proposta: `fact_time` vem só de `campos_do_fato`, e o
  resultado da nuvem fica como evidência.

## 8. O que fica para o dono e para a TEMPO-E-LUGAR

1. **A base da publicação tem de chegar à função.** Sem ela, a D63 dá sempre NAO SEI nas relativas.
2. **Colunas `fact_location_kind` / `fact_time_kind` / `_precision`** na Sala: hoje só vão escritas na base.
3. **O dono único da conta D63** (secção 7).
4. **Q2**: as palavras da secção 6 — trazer da Itália (hoje não existe lá) ou autorizar editar aqui.
   A «palavra inteira» nas âncoras também devia ir para o leitor.
5. **Comuni**: não há lista no repositório.
6. **Sicília e Emilia-Romagna**: tirar `produzione` tirou 13 lugares — 11 errados e 2 certos (Sicília,
   «riduzione della produzione»; Emilia-Romagna, «valore della produzione agricola»).
   Para o recuperar sem os erros, precisa de «produzione di <cultura>» — pede uma lista de culturas,
   que não fiz.
