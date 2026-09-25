# RELATÓRIO · LUGAR-E-TEMPO-DO-FATO (D61) · ramo `lugar-fato-v1`

Missão: `fact_location` e `fact_time` **a partir do texto**, com evidência. Pelo ACRESCENTO da
coordenação, esta bancada faz **só o extrator** (função pura, com testes); a TEMPO-E-LUGAR faz o
encanamento de ponta a ponta e liga a função.

Base: produção `origin/servico-20260923-0923` (`df0865e6`). Rede fechada. O vivo e a Sala não foram
tocados — a Sala foi lida por um único `SELECT` só-leitura (78 linhas de `sala_de_espera`), guardado
**fora do Git** em `C:/Users/London1/lugar-fato/sala-78.json`.

## 1. A interface (o que a TEMPO-E-LUGAR liga)

```python
from leis.fato_do_texto import campos_do_fato      # ou sys.path + import fato_do_texto
r = campos_do_fato(texto, publication_time=None, publication_time_basis=None)
r["fact_location"]        # "NAO SEI"  ou  "Grosseto ; Siena"   (todos, separados por " ; ")
r["fact_location_basis"]  # "CITADO · PROVINCE · âncora «constatata» · CONFIRMED_FOCUS · «trecho»"  ou  "NAO SEI · porquê"
r["fact_time"]            # "NAO SEI"  ou  a data como o texto a diz ("12 settembre", "campagna 2026", "2026-W38")
r["fact_time_basis"]      # "AMARRADO_AO_ACONTECIMENTO · DATE_EXACT · «trecho»"  ou  "RELATIVA_A_PUBLICACAO · …"  ou  "NAO SEI · porquê"
r["EVIDENCIA"]            # {LUGARES:[…], TEMPO:{…}|None, LINHAS_DE_CORPO:n, PUBLICACAO_USADA:"AAAA-MM-DD"|None}
```

- Os quatro nomes são os das colunas da Sala e do tradutor da porta (`coleta/ingresso.py:314-331`).
- **Não recebe `SOURCE_LOCATION`.** Não existe caminho para o lugar da fonte virar lugar do facto.
- `publication_time` só serve para **ancorar** «oggi / ieri / la settimana scorsa». Só conta se for
  data ISO **e** `publication_time_basis` não for `NAO SEI`/`UNKNOWN`. Nunca vira `fact_time`.
- Ponto de ligação sugerido (achado da TEMPO-E-LUGAR, `ACHADO-TEMPO-E-LUGAR-0932.txt`): onde o item
  nasce para a Admissão (`orquestrador/orquestrador.py:572-577`) ou em `admissao/admissao.py:1893-1918`,
  que hoje escreve `NAO SEI` por falta. A escolha do sítio é da TEMPO-E-LUGAR.

## 2. O que a função faz (e o que não faz)

**Não há um segundo leitor.** Quem lê o italiano é `leis/fato_local.py` (portado da Itália, «repuxar,
não editar») — já exerce a lei de `leis/lugar_do_fato.py`: menção ≠ facto, lista territorial ≠ facto,
publicação ≠ tempo do facto, vários lugares = vários. `leis/fato_local.py` **não foi editado**.

À volta dele, `leis/fato_do_texto.py` põe três coisas, todas medidas nas 78:

1. **O corpo, não a página.** Linha com menos de 8 palavras (menu, título de secção) ou com cara de
   rodapé (morada, CAP, tel, p.iva, cookie, registro stampa…) não alimenta nem lugar nem tempo.
2. **Relativo só ancorado.** Sem publicação provada, «oggi» é descartado. O leitor sozinho dava
   «oggi» como tempo do facto em 3 itens sem data de publicação nenhuma.
3. **O que não é tempo do facto é tapado antes de perguntar ao leitor**: série de anos
   («2024, 2025 e 2026»), carimbo de lista no início da linha («1 Settembre 2026 Risultati…»),
   fim de prazo («fino a novembre», «entro il 30 settembre»).

## 3. Lista de lugares: o que existe e o que falta (dito, não escondido)

Não existe no repositório uma lista oficial de comuni. A que existe é o `GAZETTEER` de
`leis/fato_local.py`: **20 regiões + 85 províncias** (das 107) + o país, declaradas como cobertura parcial por
esse ficheiro (`cobertura()`). Não se acrescentou lista nenhuma aqui — acrescentar é repuxar da Itália.
Consequência: **comune nunca sai** (só região/província; o comune que é capital de província sai como província), e 22 províncias não são reconhecidas — ficam invisíveis, não recusadas.

## 4. A medida nas 78 da Sala (`scripts/lugar_fato/MEDIDA-LUGAR-TEMPO-78-V1.json`)

`PUBLICATION_TIME` está `NAO SEI` nas 78 linhas da Sala, por isso nenhuma relativa foi resolvida.

| campo | saem de NAO SEI | certos (lidos à mão) | errados |
|---|---|---|---|
| `fact_location` | **1 de 78** | 1 (IT-T3-008, Puglia) | 0 |
| `fact_time` | **13 de 78** | 11 | 2 |
| (leitor sozinho, lugar) | 1 de 78 | — | — |
| (leitor sozinho, tempo) | 18 de 78 | — | inclui «oggi» sem publicação e datas de lista/série/prazo |

Os 2 errados que ficam (por isso a taxa de erro é **2 em 13**, cerca de 15%):
- IT-T3-010 «luglio»: é um **conselho** («eseguire la diagnosi precoce in luglio»), não o tempo de algo que aconteceu.
- IT-T10-018 «2025»: é o **ano de comparação** de um preço («sotto i 2,80 euro/kg del 2025»).

Antes das três proteções eram 15 datas com 4 erradas (luglio, série 2024-2026, «novembre» de
«fino a novembre», carimbo «1 settembre 2026» de lista).

### 4.1 O que ficou NAO SEI e não devia — depende do que se chama «facto»

Li à mão, pelos trechos, as linhas que ficaram `NAO SEI` mas têm lugar citado ou data escrita no corpo.
**A classificação é minha, uma pessoa só, a partir de trechos — pode ter erro de um ou dois itens.**

O leitor recusa **de propósito** lugar de congresso/feira/workshop, de mercado, de sede e o âmbito do
próprio boletim («della provincia di Salerno») — são falsos positivos medidos no Brasil. Por isso há
duas contagens, e **qual vale é decisão do dono**:

| leitura de «facto» | lugar em falta | tempo em falta |
|---|---|---|
| **A · a da lei atual**: só acontecimento agronómico (praga, doença, tempo, colheita, preço medido) | ~3 de 78 (IT-T3-008 chuva por região; IT-T2-034 pólen da oliveira nas Marche; IT-T10-018 danos de eventos extremos no Veneto/E-R) | ~3 de 78 (IT-T3-008 «martedì 1 settembre» e «mercoledì 9 settembre», chuva; IT-T10-018 «rilevazione … effettuata oggi 22 settembre») |
| **B · larga**: também eventos, feiras, aberturas de loja, cursos | ~19 de 78 | 20 de 33 linhas com data no corpo |

Nas 33 linhas com data no corpo, 13 são corretamente `NAO SEI`: data do próximo boletim (2),
prazo (1), leis e regulamentos (10: «Legge 9 maggio 1989», «Regolamento… del 22 giugno 2022»…).

Porque falha a leitura A: as âncoras do leitor são fitossanitárias (`constatata`, `rilevata`,
`sintomi`…). «precipitazioni», «sono cadute», «esplode il polline», «eventi estremi», «rilevazione»
não estão lá. Acrescentá-las é mudar o leitor italiano — **não fiz**: é repuxar da Itália, ou
decisão do dono para o editar aqui.

## 5. Testes e mutação

- `tests/test_fato_do_texto.py` — 12 testes, verdes (`py -m unittest tests.test_fato_do_texto`).
- `scripts/lugar_fato/mutar_fato_do_texto.py` → `MUTACAO-FATO-DO-TEXTO-V1.json`: **12 mutantes, 12 mortos**,
  cada um numa cópia em pasta temporária:
  M1 `source_location` copiado · M2 publicação vira `fact_time` · M3 lugar do menu (página inteira) ·
  M4 rodapé entra no corpo · M5 relativa sem publicação · M6 publicação com base NAO SEI ancora ·
  M7/M7c/M7d/M7b cada proteção de tempo desligada · M8 só o primeiro lugar · M9 base sem trecho.
- Errei uma vez: o primeiro M7 só mudava o **nome** da proteção, não a desligava — sobreviveu, e com
  razão. Refeito para desligar a expressão; morre.

## 6. Decisões que ficam para o dono

1. **`RELATIVA_A_PUBLICACAO`** não está em `lugar_do_fato.ORIGENS_DO_TEMPO`. A função usa a palavra
   (a missão pede-a), mas a lei não a tem. Acrescentá-la à lei é decisão do dono da lei.
2. **O que é «facto»** (leitura A ou B acima). Hoje o código segue a A.
3. **Âncoras novas no leitor italiano** (chuva, pólen, eventos extremos, «rilevazione»): repuxar da
   Itália ou autorizar editar aqui.
4. **Comuni**: não há lista no repositório; sem ela, `fact_location` para em província.
