# MICRO-VERIFICAÇÃO (D74) — plano de uma MICRO, não de uma onda

Ramo `micro-verif-v1`, a partir do vivo `e5cd691f` (PACOTE-TEMPO-LUGAR instalado).
- **Rede fechada nesta missão:** nenhum pedido. A Sala não foi lida.
- **Objetivo da MICRO** (quando o coordenador a mandar correr): provar que a coleta REAL, com o código
  instalado, faz chegar à Sala **itens novos** com publicação, lugar da fonte, data e lugar do facto,
  e as bases de cada um.

## 1 · A regra de escolha — escrita ANTES de medir (este commit vem antes de qualquer medida)

**Universo:** a coorte CONGELADA do vivo.
- Ficheiro: `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json`, 28 fontes.
- `sha256` do blob no commit: `06f87b97761d73281bc341d87d7a644ec0c5014a291265db2b8372732bf4977f`. É o que
  `onda_web.py` confere.
- O ficheiro no disco tem outro sha (`5401845a…`), só por causa do fim de linha do Windows (CRLF). O JSON
  é o mesmo, e a `onda_web.py` compara o conteúdo.

**Categorias** (a mesma fonte pode cumprir mais de uma, mas conta para uma só):
- **A · myfruit:** `IT-T10-018`, obrigatória.
- **B · boletim ou agência T2:** as `IT-T2-*` da coorte.
- **C · instituição de pesquisa (CNR/CREA/ENEA):** `IT-T5-160` (ibba.cnr.it), `IT-T5-167` (crea.gov.it),
  `IT-T5-185/186/187` (enea.it).
- **D · publica a data na página:** JSON-LD `datePublished`, `<meta property="article:published_time">`
  ou `<time datetime=…>`.
  - Medido **sem rede** nas matérias já guardadas no armazém do vivo (`data/collection-store/italy/<SID>/`),
    só leitura.
  - Conta a fração de matérias guardadas que têm uma dessas marcas.
  - **Não pode ser a myfruit** (queremos um segundo site a provar a data).

**Como se escolhe dentro de cada categoria, por esta ordem:**
1. Mais **alvos novos D40**. A medida é `scripts/capa_materia/medir_d40.mjs`, com os índices guardados
   em 25/09 07:30Z (`INDICES-D40-V1.json`), contra uma **cópia** do livro de observações atual do vivo.
2. Para a D: maior fração de matérias com data marcada.
3. Desempate por `SOURCE_ID`.
4. Fonte sem índice guardado = alvos novos `NAO MEDIDO`, e fica atrás das medidas.
5. **Uma fonte com 0 alvos novos medidos não é escolhida** se houver outra na categoria com ≥ 1.

**Domínios diferentes (D38):**
- as fontes escolhidas têm domínios registáveis todos diferentes;
- se a melhor de uma categoria repetir o domínio de uma já escolhida, passa-se à seguinte.

**Quantas:**
- A + B + C + D = 4.
- Junta-se **uma 5.ª** só se houver outra fonte T2 com ≥ 1 alvo novo e domínio novo. A razão: os boletins
  T2 são a outra metade da data e lugar (D61).
- Nunca mais de 6.

**Previsão:** escrita por fonte **antes** de correr: documentos novos; publicação sim/não; lugar da
fonte sim/não; data e lugar do facto prováveis.

## 2 · A regra aplicada: 5 fontes, 5 domínios, 16 pedidos

Medidas, todas sem rede:
- **alvos novos D40:** `MEDICAO-D40-MICRO-VERIF.json`. Os índices guardados em 25/09 07:30Z contra uma
  cópia do livro de observações do vivo (590 linhas, sha256 `221914a2…`).
- **data na página:** `DATA-NA-PAGINA-COORTE-V1.json` (armazém do vivo, só leitura).
- **plano:** `ONDA-WEB-SO-PLANO.json`, com `onda_web.py --so-plano` numa **cópia** do vivo (`e5cd691f` +
  os 16 livros sujos do vivo, copiados; sha256 em `C:/Users/London1/micro-verif-20260925/FOTO-LIVROS-VIVO.sha`).

| Categoria | Fonte | Porquê (pela regra) | Alvos novos no índice → documentos novos na corrida (D40 + teto D38) |
|---|---|---|---|
| A · myfruit | **IT-T10-018** myfruit.it | obrigatória | 5 → **3** |
| B · T2 | **IT-T2-034** ARPA Marche | das T2 com índice guardado, a de mais alvos novos (a IT-T2-051 tem 1) | 3 → **3** |
| C · pesquisa | **IT-T5-160** IBBA-CNR (ibba.cnr.it) | **nenhuma** fonte de pesquisa tem índice guardado: desempate por SOURCE_ID | **NAO MEDIDO → NAO SEI** |
| D · data na página | **IT-T7-017** Riunite & CIV | 37/37 matérias guardadas com data marcada (JSON-LD + meta); o maior D40 das D (19; Villoresi 13) | 19 → **3** |
| 5.ª · outra T2 | **IT-T2-051** Arpae | T2 com ≥ 1 alvo novo e domínio novo | 1 → **1** |

`--so-plano`: **PODE_CORRER = true**.
- As 5 correm, nenhuma salta pelo teto.
- **16 pedidos previstos**, no máximo 5 por domínio: myfruit.it 5 · cnr.it 5 · arpa.marche.it 2 · arpae.it 2 · riuniteciv.com 2.

## 3 · A previsão, escrita ANTES de correr

A base é o que os **leitores instalados** (`e5cd691f`) dão nas matérias **já guardadas** de cada fonte
(`PREVISAO-COM-O-INSTALADO-V1.json`). Itens novos da mesma fonte tendem a sair como os guardados.

| Fonte | Documentos novos | Publicação | Lugar da fonte | Data do facto (nas guardadas) | Lugar do facto (nas guardadas) |
|---|---|---|---|---|---|
| IT-T10-018 myfruit | **3** | **SIM**, precisão INSTANTE (meta, 53/53) | **NÃO** | 16 de 53 (EVENTO 7, CAMPO 9) → ~1 em 3 | 14 de 53 (MERCADO 8, EVENTO 5, CAMPO 1) → ~1 em 3 |
| IT-T2-034 ARPA Marche | **3** | **SIM**, INSTANTE (`<time>`, 7/7) | **NÃO** | 4 de 7 (EVENTO 3) → ~1–2 em 3 | 3 de 7 (EVENTO) → ~1 em 3 |
| IT-T5-160 IBBA-CNR | **NAO SEI** (0 a 3) | provável SIM (JSON-LD, mas só 1 guardada) | **NÃO** | 0 de 1 → provável NÃO | 0 de 1 → provável NÃO |
| IT-T7-017 Riunite | **3** | **SIM**, INSTANTE (37/37) | **NÃO** | 7 de 37 → 0–1 em 3 | 4 de 37 (EVENTO) → 0–1 em 3 |
| IT-T2-051 Arpae | **1** | **NÃO**: 0/7 com data na página, e o contrato não declara a data como EDIÇÃO → `NAO SEI` com o porquê | **NÃO** | 2 de 7 → provável NÃO | 1 de 7 → provável NÃO |

**Na Sala** entra só o que a gaveta da fonte aprovar (SIM). O REROUTE só anota (D66).

Pelas 78 da Sala: myfruit costuma passar; as agências T2, a Riunite e o CNR passam pouco.

**Previsão para a Sala: +2 a +8 linhas novas.**
- **O critério de sucesso da micro:** ≥ 1 item novo com `published_at` + base + precisão (quase certo
  pela myfruit).
- As bases dos `NAO SEI` têm de vir escritas, com o porquê, e não com o default da 033.

### ⚠️ Achado: o lugar da fonte não pode ser provado com esta coorte
`regras/contratos_de_fonte.lugar_da_fonte()` dá **`NAO SEI` para as 28 fontes da coorte**: nenhum
contrato declara `SOURCE_LOCATION_RULE`. A micro vai mostrar `source_location = NAO SEI` com o porquê,
em todos os itens novos. Isso está **certo pela regra** (nunca se inventa a sede), mas **não prova** o
caminho do lugar da fonte. Para o provar é preciso declarar a sede no contrato de ≥ 1 fonte da coorte.
É decisão à parte; não mexi.

## 4 · O comando (a correr no vivo, só quando o coordenador mandar)

```
cd <vivo: source-curator-service-v1 @ e5cd691f>
py ferramentas/big_collection/onda_web.py --correr ^
   --fontes=IT-T10-018,IT-T2-034,IT-T5-160,IT-T7-017,IT-T2-051 ^
   --sha256=06f87b97761d73281bc341d87d7a644ec0c5014a291265db2b8372732bf4977f ^
   --saida=C:\bc\micro-verif-<AAAAMMDD-HHMM>
```

- Com o mesmo ambiente da 2.ª onda (BIG-COLLECTION-RUNBOOK): portão de egresso por consenso = PASS IT
  antes, e os disjuntores da `onda_web.py`.
- **Pasta de saída nova.** Se já existir um `TETO-ONDA.json` lá dentro, a `onda_web.py` recusa.
- `--fontes` só filtra dentro da coorte congelada. Uma fonte de fora recusa a micro inteira antes da rede.

## 5 · As consultas de DEPOIS (`MICRO-VERIFICACAO-SELECTS.sql`)

- Todas são **só leitura**: `begin transaction read only … rollback`.
- Lêem a vista `sala_de_espera_atual` (033).
- Filtram as 5 fontes e `pousado_em >= :inicio`.

```
psql -X -v ON_ERROR_STOP=1 -v inicio='<INICIO ISO>' -f MICRO-VERIFICACAO-SELECTS.sql "<DSN da Sala>"
```

| Consulta | O que mostra |
|---|---|
| Q0 | linhas, última pousada e revisões da Sala. **Antes e depois**: a Sala não pode descer |
| Q1 | os itens novos |
| Q2 | `published_at` + base · `source_location` + base · `fact_time` + base · `fact_location` + base |
| Q3 | `completude_tempo_lugar` e `tempo_lugar_evidencia`: **PUBLISHED_AT_PRECISION** (aviso da SOCIAL-TEMPO), PUBLISHED_AT_CONFLITO/OUTRA, tipos e precisões da data e do lugar do facto, LEITOR, ORIGEM |
| Q4 | por fonte, quantos saem de NAO SEI em cada campo (valor **e** base) |
| Q5 | prova de que foi o **código novo** que escreveu: 0 itens novos com a ORIGEM «pousado antes da migration 033» |

**Conferidas sem rede.** Numa base Postgres **local e descartável**, com as 33 migrações do vivo
aplicadas, as 6 consultas correram sem erro sobre o esquema da 033, com 0 linhas porque a base está vazia.

## 6 · O que ficou por saber
- **Os alvos novos da fonte de pesquisa (IT-T5-160):** não há índice guardado. Os índices D40 só cobrem
  as 18 fontes da 1.ª onda.
- **Os índices guardados são de 25/09 07:30Z.** O site pode ter mais novidades hoje, o que só aumenta
  os documentos novos.
- **Quantos passam a gaveta** (entram na Sala): só a corrida o diz.
