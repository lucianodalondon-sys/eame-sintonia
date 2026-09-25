# PLANO DE INSTALAÇÃO — TEMPO-PUBLICACAO (D61)

Ramo: `claude/publication-time-source-location-ux4cuc` · base `df0865e` (produção).

```
PUBLICATION_TIME != FACT_TIME != OBSERVATION_TIME != COLLECTION_TIME
SOURCE_LOCATION  != FACT_LOCATION
```

## O que entra

| peça | ficheiro | o que faz |
|---|---|---|
| extrator | `coleta/executor_texto_de_html.py` · `tempo_de_publicacao()` | HTML → `{VALOR, BASE, PRECISAO, ORIGINAL, PORQUE}`. Ordem: JSON-LD `datePublished` → `meta article:published_time` → `<time datetime>` → data no índice. ISO 8601 com fuso; hora sem fuso fica só o DIA. Nível com duas datas diferentes cala-se (AMBIGUO). |
| saída | `publicacao_para_o_contrato()` | `PUBLISHED_AT` + `PUBLISHED_AT_BASIS` + `PUBLISHED_AT_PRECISION` (D62: INSTANTE · DIA · NAO SEI). `NAO SEI` nunca atravessa como valor; o porquê vai na BASE. Sem chave de facto. |
| lugar | `regras/contratos_de_fonte.py` · `lugar_da_fonte()` / `lugar_para_o_contrato()` | `SOURCE_LOCATION` pelo CONTRATO (`SOURCE_LOCATION_RULE` conferido no gazetteer), `BASE=CONTRATO`, `SOURCE_LOCATION_PRECISION` (D62). **Nunca** o `REGION` do Atlas (é a região de que a fonte fala). |
| contrato | `regras/italy_contracts.mjs` · `contratoGenerico` | a linha onboarded PODE declarar `SOURCE_LOCATION_RULE`. Hoje nenhuma declara (0/193): nenhum contrato muda. |
| testes | `tests/test_tempo_e_lugar_da_publicacao.py` | 42 testes; HTML reais de `data/collection-store/italy/`. |

**Efeito em runtime ao instalar: nenhum.** Ninguém chama as funções novas ainda —
o encanamento dos 7 passos (derivado → estruturação → porta → admissão → Sala,
colunas `*_basis`) é da bancada local TEMPO-E-LUGAR. Sem migração, sem Sala.

## Instalar (numa linha que o dono autorize)

```bash
git fetch origin claude/publication-time-source-location-ux4cuc
git cherry-pick <SHA do commit "D61 tempo-publicacao: extrator ...">
python3 -m unittest tests/test_tempo_e_lugar_da_publicacao.py      # 42 OK
python3 system-map/scripts/correr_a_cadeia.py REGERAR
python3 system-map/scripts/correr_a_cadeia.py VALIDAR               # SYSTEM_MAP_CHECK=PASS
git add system-map/data italia-portale/client/system-map docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md
git commit -m "mapa: regerado pela cadeia (tempo-publicacao D61)"
python3 system-map/scripts/impressao_da_arvore.py --conferir-carimbo  # IGUAL
```

Para o encanamento: `item["PUBLISHED_AT*"]` = `publicacao_para_o_contrato(tempo_de_publicacao(bytes_do_html))`;
`item["SOURCE_LOCATION*"]` = `lugar_para_o_contrato(lugar_da_fonte(source_id))`.
`FACT_TIME`/`FACT_LOCATION` não se tocam.

## Desfazer

```bash
git revert <SHA do commit do extrator>
python3 system-map/scripts/correr_a_cadeia.py REGERAR && python3 system-map/scripts/correr_a_cadeia.py VALIDAR
git add system-map/data italia-portale/client/system-map docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md && git commit -m "mapa: regerado (revert D61)"
```

Nada no banco a desfazer.

## DA-6 (coordenador, 25/09) — um dono para o facto

FACT_TIME / FACT_LOCATION a partir do texto (incluindo as datas relativas da D63/D64) têm
**um dono só: o extrator local `lugar-fato-v1`**. Este ramo é dono **só** de PUBLICATION_TIME
(+ base, precisão) e SOURCE_LOCATION (+ base). A conta relativa fica como **evidência**
(`RELATIVE_TIME_*`), sem escrever `fact_time`. O teste `test_DA6_nenhuma_saida_deste_ramo_escreve_facto`
reprova qualquer saída com chave `FACT_*` e qualquer chave de facto escrita no código dos dois módulos.

## D62 (dono, 25/09) — como isto obedece

- **Nada é obrigatório.** Nenhuma função levanta nem reprova por faltar data ou lugar;
  devolvem sempre um recibo. O encanamento **não** pode usar `NAO SEI` como motivo de
  descarte — é só precisão menor.
- **A precisão viaja** (`*_PRECISION`) para a Intelligence saber o grau de cada item.
- ~~Data relativa não vira data~~ — **substituído pela D63** (abaixo). Continua verdade só
  para a PUBLICAÇÃO: ela nunca sai de «ieri».

## D63 (dono, 25/09 ~11:08) — data relativa conta, a partir da publicação

| peça | o que faz |
|---|---|
| `conta_relativa_a_publicacao(texto, publicacao)` | só com PUBLICATION_TIME **provada** (com BASE). «ieri» → dia exacto; «l'altro ieri», «N giorni fa» → dia; «la (scorsa) settimana scorsa», «N settimane fa» → intervalo ISO seg–dom `início/fim`; «il mese scorso» → intervalo do mês. Nunca um dia inventado dentro de um intervalo. |
| `evidencia_relativa(r)` | **DA-6: só evidência, nunca FACT_TIME.** `RELATIVE_TIME_EXPRESSION` + `RELATIVE_TIME_COMPUTED` + `RELATIVE_TIME_PRECISION` (`CALCULADA:DIA/SEMANA/MES`) + `RELATIVE_TIME_BASIS = "RELATIVA_A_PUBLICACAO «<expressão>»"`. |

- Sem publicação provada → NÃO SEI. Duas contas diferentes no mesmo texto → NÃO SEI (AMBIGUO).
- Fora, até haver caso medido: «l'anno scorso» (comparação de safra).

## D64 (dono, 25/09) — «oggi» e a interface do item

- «oggi» conta (0 dias, `CALCULADA:DIA`) **só** quando o texto diz que é o próprio dia:
  «oggi, lunedì» (e o dia da semana tem de bater com a publicação — senão NÃO SEI) ou
  «oggi è stato/a». Hoje-em-dia («ad oggi», «al giorno d'oggi», «oggi i consumatori») = NÃO SEI.
- `publicacao_do_item(item)` lê `publication_time` + `publication_time_basis` (ou
  `published_at`/`PUBLISHED_AT` + `_basis`) da interface do item. Valor sem base, base
  `NAO SEI —…`, ou dois nomes a contradizerem-se = sem publicação provada = sem conta.
- A publicação fica à parte e intacta; `leis/artefato.py::conferir` aceita a conta (≠ publicação).
- Medido no armazém: 1 caso real (IT-T3-005, «le piogge della scorsa settimana») — e a página
  não tem data de publicação, logo fica NÃO SEI. Contrato de saída ganha `FACT_TIME_PRECISION`:
  (substituído pela DA-6: é `RELATIVE_TIME_PRECISION`, evidência).

## Limites declarados (NÃO SEI)

- **Data no índice**: o 4.º nível existe (`data_no_indice=`), mas **nenhum produtor a
  entrega** — o coletor não a lê do índice e `raw_asset` não tem coluna. Fica NÃO SEI.
- **Lugar**: o contrato só prova 10 de 206 fontes (sedes nos 13 contratos à mão; Terlano,
  San Michele, «site nacional», «ITALIA» ficam fora do gazetteer). As 193 onboarded
  dizem NÃO SEI até a curadoria declarar a sede na linha.
- PDF não passa por aqui (o extrator é de HTML).
