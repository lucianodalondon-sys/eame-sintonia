# AUDITA-T8-V1 — data de publicação, lugar da fonte e saúde animal nas 20 fontes que a receita-t8 liga

> Só leitura. Base: produção `servico-20260923-0923` @ **`e5cd691f`** (PACOTE-TEMPO-LUGAR instalado).
> Rede fechada. Sala real só com `SELECT` (sessão `default_transaction_read_only = on`). Vivo intocado.

| o que mediu | com quê (instalado em e5cd691f) |
|---|---|
| data de publicação | `coleta/executor_texto_de_html.py:380` `tempo_de_publicacao()` — JSON-LD → meta → `<time>` → índice; ambíguo = NAO SEI |
| lugar da fonte | `regras/contratos_de_fonte.py:253` `lugar_da_fonte()` — **só o contrato** (`SOURCE_LOCATION_RULE`), nunca o `REGION` do Atlas |
| saúde animal / veterinária (D48) | contagem de palavras nas páginas guardadas (saúde: veterinar, vaccin, malatti, patolog…; produção: allevament, zootecn, latte, suini…) |

**O que estava guardado:** a Sala real tem **0** RAW destas 20 fontes (medido agora). As únicas
páginas guardadas são as do gabarito do detector de capa (`~/ld2-controlo/bytes`,
`~/detector-capa-gabarito/bytes`, fora do Git) — **9 das 20** têm uma página de matéria. sha256 de
cada uma em `data/derivados/AUDITA-T8-V1/AUDITA-20.json`.

## A tabela

| fonte | página guardada | publicação | base | lugar da fonte | saúde animal (D48) |
|---|---|---|---|---|---|
| IT-T8-021 Terra e Vita | não | NÃO MEDIDO | — | **NÃO SEI** (contrato não declara) | não medido |
| IT-T8-022 Terra e Vita (colture) | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T8-024 Terra e Vita (seminativi) | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T8-028 Frutticoltura | sim | **SIM** 2026-09-14 | JSON-LD `datePublished` | NÃO SEI | não (saúde 2 · produção 9) |
| IT-T8-029 Contoterzista | sim | **NÃO SEI** | `<time>` **ambíguo**: 10 datas — a página guardada é de um **autor**, não uma matéria | NÃO SEI | não |
| IT-T8-030 Informatore Zootecnico | sim | **SIM** 2026-09-17 | JSON-LD | NÃO SEI | **produção animal** (0 · 69) — fica |
| IT-T8-034 Macchine Agricole | sim | **SIM** 2026-09-02 | JSON-LD | NÃO SEI | não |
| IT-T8-039 Orticoltura | sim | **SIM** 2026-09-17 | JSON-LD | NÃO SEI | não (os 4 «saúde» são «salute del suolo») |
| IT-T8-040 Suinicoltura | sim | **SIM** 2026-09-10 | JSON-LD | NÃO SEI | **produção animal com conteúdo veterinário** (17 · 27): a página é de uma vacina para leitões |
| IT-T8-041 Vigne Vini e Qualità | sim | **SIM** 2026-08-30 | `<time datetime>` | NÃO SEI | não |
| IT-T8-042 Terra e Vita (viticoltura) | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T8-051 Terra e Vita | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T8-068 Terra e Vita (home) | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T12-024 Regione Veneto | sim | **NÃO SEI** | nenhuma marca (sem JSON-LD, meta nem `<time>`) | NÃO SEI | não |
| IT-T12-104 Geoportale Lombardia | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T12-117 Calabria Impresa (energia) | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T12-129 Regione Sicilia | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T12-130 Terra e Vita (PAC/PSR) | sim | **SIM** 2026-08-26 | JSON-LD | NÃO SEI | não |
| IT-T12-131 terraevita.it (PAC) | não | NÃO MEDIDO | — | NÃO SEI | não medido |
| IT-T12-137 PSRN | não | NÃO MEDIDO | — | NÃO SEI | não medido |

A missão falava em «6 T12»; as fontes T12 que a receita liga são **7** (a 7.ª é IT-T12-137, PSRN).
Estão todas na tabela.

## O que isto diz

1. **Publicação:** das 9 páginas guardadas, **7 SIM** (6 por JSON-LD, 1 por `<time>`), **2 NÃO SEI**
   com razão escrita pelo extrator. As outras 11 fontes **não têm página guardada** — medir exige
   rede (a MICRO).
2. **Lugar da fonte: NÃO SEI nas 20.** Não é o extrator que falha: é o **contrato** que não declara
   `SOURCE_LOCATION_RULE` (o porquê escrito é esse, fonte a fonte). As 13 Edagricole têm a sede
   no rodapé (Via Eritrea 21, 20157 Milano) — mas a lei instalada só aceita o contrato. **Gap da
   Collection:** declarar `SOURCE_LOCATION_RULE` nos contratos destas fontes (uma linha por
   fonte; para as Edagricole é a mesma).
3. **Saúde animal / veterinária como foco: 0.** Ninguém sai pela D48. Produção animal: **IT-T8-030**
   (fica) e **IT-T8-040** (fica, mas traz páginas veterinárias — decisão já pedida na RECEITA-T8).
   11 fontes sem página: não medido.

## Correção de uma entrega minha anterior

No relatório curto da RECEITA-T8 (lista de 10, `RECEITA-T8-TEMPO-E-LOCAL-10.txt`) escrevi
**IT-T8-029 «SIM 23/02/2026 por `<time>`»**. **Estava errado.** A minha leitura caseira pegou a
primeira de 10 datas de uma página de autor. O extrator instalado vê a ambiguidade e diz NÃO SEI —
que é o certo. E lá também dei o **local da fonte** como «SIM Milano, pelo rodapé»: pela lei
instalada (só o contrato), é **NÃO SEI**; Milano é um facto do rodapé, não um valor declarado.

## Em palavras simples

- Das 20 fontes, só 9 têm uma página guardada. Em 7 delas a data de publicação está clara; em 2
  não dá para saber (uma é página de autor com 10 datas, a outra não tem data nenhuma).
- O lugar da fonte fica «não sei» em todas: os contratos destas fontes não dizem onde fica quem
  publica. Basta acrescentar essa linha aos contratos (para a Edagricole é Milão).
- Nenhuma é de saúde animal. Uma revista de porcos às vezes publica sobre vacinas — já está
  anotado para decidir.
- Corrigi um erro meu de antes: tinha dado uma data a uma página que, afinal, é ambígua.
