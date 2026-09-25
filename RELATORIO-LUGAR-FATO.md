# RELATÓRIO · LUGAR-E-TEMPO-DO-FATO (D61 + D62 + D63) · ramo `lugar-fato-v1`

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

## 1. A interface (o que a TEMPO-E-LUGAR liga)

```python
from leis.fato_do_texto import campos_do_fato      # ou sys.path + import fato_do_texto
r = campos_do_fato(texto, publication_time=None, publication_time_basis=None)
r["fact_location"]            # "NAO SEI"  ou  "Grosseto ; Siena"   (todos do MESMO tipo, " ; ")
r["fact_location_basis"]      # "CAMPO · CITADO · PROVINCE · âncora «constatata» · CONFIRMED_FOCUS · «trecho»"  ou  "NAO SEI · porquê"
r["fact_location_kind"]       # CAMPO | EVENTO | MERCADO | NAO SEI
r["fact_location_precision"]  # COUNTRY | REGION | PROVINCE | NAO SEI
r["fact_time"]                # "NAO SEI" | "12 settembre" | "12-13 novembre 2026" | "2026-09-22" | "2026-09-14/2026-09-20"
r["fact_time_basis"]          # "CAMPO · AMARRADO_AO_ACONTECIMENTO · DATE_EXACT · «trecho»"
                              # "RELATIVA_A_PUBLICACAO · CAMPO · DATE_EXACT+CALCULADA · «ieri» contado a partir da publicação provada 2026-09-23 (…) · «trecho»"
                              # "NAO SEI · porquê (e as expressões relativas guardadas)"
r["fact_time_kind"]           # CAMPO | EVENTO | NAO SEI
r["fact_time_precision"]      # DATE_EXACT | WEEK | MONTH | SEASON | APPROXIMATE | NOT_KNOWN, com "+CALCULADA" quando veio da conta
r["EVIDENCIA"]                # LUGARES (todos, de todos os tipos, cada um com KIND, PAPEL_NA_LEI e trecho),
                              # TEMPO, TEMPOS_DE_EVENTO, EXPRESSOES_RELATIVAS, PUBLICACAO_PROVADA (à parte), LINHAS_DE_CORPO
```

- `fact_location`, `fact_location_basis`, `fact_time` e `fact_time_basis` são as colunas da Sala e do
  tradutor da porta (`coleta/ingresso.py:314-331`). `_kind` e `_precision` **não têm coluna na Sala**:
  vão também escritos no início da `_basis`. Criar colunas é decisão da TEMPO-E-LUGAR e do dono.
- **Não recebe `SOURCE_LOCATION` nem a data de coleta.** Não há caminho para nenhum dos dois entrar.
- `publication_time` conta só se for data ISO **e** `publication_time_basis` não for vazia nem
  `NAO SEI`/`UNKNOWN`. Serve para duas coisas: descartar a data do texto que é o carimbo da publicação,
  e fazer a conta das relativas. Sozinha nunca vira `fact_time`. ⚠️ A Sala hoje **não guarda a base
  da publicação**: sem ela, nenhuma relativa é contada. A TEMPO-E-LUGAR tem de passar a base.
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
   - «eventi estremi / meteorologici / atmosferici» não é evento técnico, é tempo no campo.
3. **Data de EVENTO.** Numa frase com palavra de evento: «12 e 13 novembre 2026», «dal 6 all'8 ottobre»,
   «16-24 maggio», «8 ottobre 2026». Intervalo → `APPROXIMATE` com o intervalo escrito; um dia → `DATE_EXACT`.
   Ordem: data explícita de CAMPO > relativa de CAMPO > data de EVENTO > relativa de EVENTO.
4. **Relativas (D63).** Com publicação provada, e só se a frase estiver presa a um facto (palavra de
   campo do leitor ou palavra de evento):

   | expressão | conta | precisão |
   |---|---|---|
   | oggi, stamattina, stamane, stasera, stanotte | o dia da publicação | DATE_EXACT+CALCULADA |
   | ieri · l'altro ieri · domani · dopodomani | −1 · −2 · +1 · +2 dias | DATE_EXACT+CALCULADA |
   | lunedì scorso … domenica scorsa | o último desse dia **antes** da publicação | DATE_EXACT+CALCULADA |
   | la settimana scorsa / la scorsa settimana | **segunda a domingo** da semana anterior | WEEK+CALCULADA |
   | questa settimana · la prossima settimana | segunda a domingo da semana | WEEK+CALCULADA |
   | il mese scorso | 1.º ao último dia do mês anterior | MONTH+CALCULADA |
   | l'anno scorso | 1/1 a 31/12 do ano anterior | APPROXIMATE+CALCULADA |
   | nei giorni scorsi · di recente · recentemente | **sem medida**: fica como evidência, nunca vira data | — |

   Intervalo em ISO 8601 (`2026-09-14/2026-09-20`): **nunca um dia inventado dentro dele**. Sem
   publicação provada = `NAO SEI`, e a expressão fica na EVIDENCIA e na base.
5. **O que não é tempo do facto é tapado**: série de anos, carimbo de lista no início da linha, prazo.

## 3. Lista de lugares: o que existe e o que falta

Não existe no repositório uma lista oficial de comuni. A que existe é o `GAZETTEER` de
`leis/fato_local.py`: **20 regiões + 85 províncias** (das 107) + o país. Não acrescentei lista
nenhuma: a regra é trazer da Itália. **O ramo da Itália (`claude/sintonia-italy-pilot-b1l401`) já não tem
`leis/fato_local.py`** (foi apagado lá), portanto hoje não há versão para puxar. Consequência:
comune nunca sai (o capoluogo sai como província), 22 províncias ficam invisíveis, e lugares fora da
Itália (Madrid) também.

## 4. A medida nas 78 da Sala (`scripts/lugar_fato/MEDIDA-LUGAR-TEMPO-78-V1.json`, DATASET V2)

A Sala não guarda a base da publicação → **nenhuma relativa pôde ser contada** (é o certo pela D63).
Das 78 linhas, 18 têm expressão relativa e 6 têm uma presa a um facto; com a publicação provada, essas 6
poderiam ganhar data.

| campo | saem de NAO SEI | por tipo | antes (D61) |
|---|---|---|---|
| `fact_location` | **12 de 78** | CAMPO 1 · EVENTO 7 · MERCADO 4 | 1 de 78 |
| `fact_time` | **20 de 78** | CAMPO 13 · EVENTO 7 | 13 de 78 |

### 4.1 Leitura à mão — li as 32 respostas (12 lugares + 20 datas)

**A classificação é minha, uma pessoa só, pelos trechos. Pode ter erro de um ou dois.**

**Lugar, 12 de 78:**
- **certos, 6**: IT-T3-008 Puglia (CAMPO) · IT-T5-015 Napoli (EVENTO, 2 linhas) · IT-T10-018 Milano
  (MERCADO) · IT-T10-018 Piemonte/Lombardia (MERCADO — são aberturas de supermercado; o lugar está
  certo, o tipo é discutível) · IT-T5-090 Roma/Milano/Brescia/Padova/Napoli (EVENTO — congressos
  certos, mas de demografia, não de agro).
- **meio certos, 3**: IT-T5-010 (Ferrara certo, Veneto/Italia/Roma de outras frases) · IT-T10-018
  Sicilia/Verona (Verona é o mercado; a Sicília é onde a produção caiu, isso é CAMPO) · IT-T10-018
  Rimini/Piemonte/Italia (Rimini certo).
- **errados, 3**: IT-T5-033 «Italy» (2 linhas; o trecho não diz onde é o evento) · IT-T10-018
  Sardegna (é onde se produzem morangos, CAMPO, não mercado).

**Data, 20 de 78:**
- **certas, 14**: campagna 2010 · 12-13 novembre 2026 (×2) · 8 ottobre 2026 (×2) · raccolta 2026 ·
  stagione 2026 · 2025 (meta dos retalhistas) · 23 settembre 2026 · 1-4 febbraio 2023 · 2025 (verba da
  Região) · 6-8 ottobre 2026 · 20-22 aprile 2027 · maggio (pólen).
- **data certa, tipo errado, 2**: IT-T5-033 «29 settembre 2026» (×2) é o dia de um evento e saiu CAMPO.
- **erradas, 4**: IT-T3-010 «luglio» (é conselho) · IT-T10-018 «2025» (ano de comparação de preço) ·
  IT-T5-029 «2022» (início de um curso) · IT-T5-049 «21 settembre» (exame adiado).

Em números: lugar certo ou meio certo em **9 de 12**; data certa em **14 de 20** (16 de 20 contando
o valor sem o tipo). Antes de consertar, nesta mesma leitura, achei e corrigi 2 erros meus:
«fermo» (parado) virava a província de **Fermo**, e «eventi estremi» virava evento técnico.

## 5. Testes e mutação

- `tests/test_fato_do_texto.py` — **23 testes, verdes** (`py -m unittest tests.test_fato_do_texto`):
  corpo/rodapé, assinatura sem SOURCE_LOCATION nem data de coleta, vários lugares, EVENTO e MERCADO
  nunca CAMPO, CAMPO vence EVENTO, cada expressão relativa com a conta (numa quarta-feira, 23/09/2026),
  intervalo nunca vira um dia, sem publicação provada = NAO SEI (4 formas de «não provada» × 3
  expressões), «nei giorni scorsi» sem medida, relativa de evento («domani»), conta num 29 de fevereiro.
- `scripts/lugar_fato/mutar_fato_do_texto.py` → `MUTACAO-FATO-DO-TEXTO-V1.json`: **21 mutantes, 21 mortos**.
  Só conta como morto se **um teste falhou** (asserção); erro de execução não conta.
  M1 source_location copiado · M2 publicação vira fact_time · M3 menu conta · M4 rodapé conta ·
  M5 relativa sem base da publicação · **M5b a conta usa a data de coleta (hoje) em vez da publicação** ·
  M5c a função aceita a data de coleta como reserva · M6 base NAO SEI ancora · M7/M7c/M7d cada proteção
  de tempo desligada · M8 só o primeiro lugar · M9 base sem trecho · M10 evento vira CAMPO · M11 mercado
  vira CAMPO · M12 evento passa à frente de CAMPO · M13 semana vira um dia · M14 «nei giorni scorsi» vira
  data · M15 precisão esconde CALCULADA · M16 «fermo» volta a ser Fermo · M17 «eventi estremi» vira evento.
- Errei duas vezes, e corrigi: o primeiro M7 só mudava o **nome** da proteção (sobreviveu, e com razão);
  o primeiro M5 «morria» por **erro de execução**, não por um teste — não provava nada. Refeitos.

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

## 7. O que fica para o dono e para a TEMPO-E-LUGAR

1. **A base da publicação tem de chegar à função.** Sem ela, a D63 dá sempre NAO SEI nas relativas.
2. **Colunas `fact_location_kind` / `fact_time_kind` / `_precision`** na Sala: hoje só vão escritas na base.
3. **«oggi» quer dizer muitas vezes «hoje em dia»** («oggi la frutticoltura…»). Com a publicação
   provada, a conta dá o dia da publicação — que na prática é a data de publicação a entrar pela porta
   de trás. Só acontece quando a frase tem palavra de facto e não há data explícita. Nas 78: as 6 linhas
   com relativa presa a um facto têm todas um «oggi» (5 de CAMPO, 1 de EVENTO). A D63 manda contar «oggi»; aviso o risco, **não** o tirei.
4. **Q2**: as palavras da secção 6 — trazer da Itália (hoje não existe lá) ou autorizar editar aqui.
5. **Comuni**: não há lista no repositório.
