# PESQUISADORES-CONTEUDO (D92) — materiais dos pesquisadores até à Sala

Ramo `pesq-fora-do-mur-v1`, **sobre o vivo `554c1ec1`**. **Sem rede** nesta missão: tudo o que sai à rede é
comando para o coordenador. Vivo e Sala não tocados. **SEM MAPA** (as peças estão declaradas; a cadeia não correu).
Saída fora do Git: `C:/Users/London1/sintonia-sala-italia/pesquisadores-conteudo/`.

## Em palavras simples

1. **OpenAlex (a porta oficial para robôs, D91).**
   - Dois pedidos por lote: **131 pesquisadores**, 50 por pedido, para saber onde trabalham hoje e os
     temas; e as **obras desde 2024** dos **62 prioritários**, 200 por página.
   - A 1.ª rodada são **5 pedidos, 5 de 5**. O ORCID **não** é pedido: o ORCID de cada pessoa já está
     nos nossos livros.
   - As páginas ficam guardadas **no mesmo formato** que a estrada T6 → Sala já lê. Provado sem rede com
     registos reais: 3 de 3 colhidos, SUCCESS.
2. **Páginas de grupos e laboratórios.**
   - Começa nas **24** páginas de departamento/instituto que **já estão** na nossa fila. 4 são do CNR, que
     continua fechado.
   - Segue só ligações que dizem «laboratorio / gruppo di ricerca / research group», e só dentro da mesma
     casa. Respeita o robots.
   - Guarda o **feed que a página declara**. Um feed que a página não declara não se adivinha.
3. **Os 100 estudos T6 na Sala:** o ensaio **já foi feito** hoje, das 22:03 às 22:20, numa cópia da Sala:
   **+100**, e a 2.ª passagem dá +0. O que falta está na §3. Não falta rede nem código novo.

⚠️ Não sei ainda:
- **quantas obras** vão chegar (pelo menos **95**, as recentes dos prioritários que já estão na T6);
- **quantos grupos têm feed**: nenhum livro nosso mediu isso.

## 0 · Os livros de hoje (26/09): pedidos por domínio, conferidos

| Domínio | Pedidos hoje | Rodadas (hora de Brasília) | Máximo numa rodada | Regra |
|---|---|---|---|---|
| `api.openalex.org` | **21** | 10:20 (5), 10:4x (5), 11:0x (2), 13:59 (5), 14:00 (4) | 5 | 5 por rodada; **sem** teto de 24 h (a D90 só o pôs no ORCID) |
| `api.crossref.org` | **20** | 10:20, 10:43, 11:04, 14:01 (5 cada) | 5 | 5 por rodada |
| `pub.orcid.org` | **25** | 10:20, 10:4x, 11:0x (5 cada), 14:00 (4), 19:58 (1, o meu acidente), 20:18 (5, lista-mestra) | 5 | **5 por 24 h (D90)**: gasto até 27/09 às 20:20 (marcado no contador) |

Fontes: `pesquisadores-t6/rede/ESTADO.json`, `consulta2/RODADA-C2-1/2.json`,
`lista-mestra/RODADA-LISTA-1.json`, `seguir-pesquisadores/CONTADOR-24H.json`, e a hora dos ficheiros.

- O `contador.py` passou a escrever OpenAlex e Crossref **sem** teto de 24 h (`None`): conta-os, mas não
  os bloqueia.
- O ORCID continua em 5 por 24 h. As páginas comuns continuam em 5 por domínio por 24 h.

## 1 · OpenAlex (`openalex_conteudo.py`)

**Quem (sem rede):**
- **69** vêm da lista-mestra: a busca ORCID em lote das 20:18 deu **72** pessoas com ORCID, e **3** têm 2
  ORCID cada. Esses 3 ficam **fora** (ambíguo não se usa).
- **62** são prioritários com um ORCID só (`PESSOAS-ORDENADAS.json`; Grassi não tem ORCID).
- Os dois grupos não se sobrepõem: dá **131 autores**.

| Pedido | Endereço | Quantos |
|---|---|---|
| A. Autores | `/authors?filter=orcid:A\|B\|…` (50), `select` = instituição atual, afiliações, temas, contagens | **3 pedidos** (131 ÷ 50) |
| B. Obras | `/works?filter=author.orcid:A\|B\|…,from_publication_date:2024-01-01`, 200 por página, cursor | 2 grupos (50 + 12). Pelo menos 1 página cada; o total **NÃO SEI** até à 1.ª (o `meta.count` diz) |

- **Rodada 1 = 3 + 2 = 5 pedidos.** As seguintes continuam pelo cursor guardado.
- Registos das obras **completos**, sem `select`, porque o executor T6 precisa de autoria e resumo.
- Cada página é guardada tal como veio (RAW, sha256 no `PEDIDOS.json`), com o nome
  `openalex-PESQUISADORES-g<grupo>-p<página>.json`.
- **Prova de que a estrada T6 as lê** (sem rede): usei o `coleta/pesquisadores_t6_executor.py` do ramo
  `t6-para-sala-v1`, numa árvore temporária, com uma página feita de 3 registos reais de hoje.
  - `resposta_valida` = True. `colher` = **SUCCESS, 3 colhidos, 0 erros**.
  - A cultura e o problema foram lidos do texto.
  - ⚠️ Diferença, declarada: o campo «par da consulta escrito no texto» fica vazio, porque a consulta é
    por pessoa e não por par.
- `--medir` (sem rede, não toca no RAW) conta: autores achados, sem registo, ORCID em 2 IDs do OpenAlex,
  obras distintas, **com resumo**, **com PDF aberto**, acesso aberto, só título, e quantas já estão nos 589.

```bash
A=C:/Users/London1/sintonia-sala-italia
# o plano (JA FEITO; sem rede): 131 autores, 3 lotes, 2 grupos de obras
py ferramentas/seguir_pesquisadores/openalex_conteudo.py --plano --lista-mestra=$A/pesquisadores-t6/lista-mestra \
   --pessoas=$A/seguir-pesquisadores/PESSOAS-ORDENADAS.json --saida=$A/pesquisadores-conteudo/openalex
# rodada (VPN IT; portao antes e depois; <= 5 a api.openalex.org). Repetir ate "FALTA" dar 0 e 0
py ferramentas/seguir_pesquisadores/openalex_conteudo.py --rodada --autorizado --saida=$A/pesquisadores-conteudo/openalex
# a medida (sem rede)
py ferramentas/seguir_pesquisadores/openalex_conteudo.py --medir --saida=$A/pesquisadores-conteudo/openalex \
   --t6=$A/pesquisadores-t6/rede/UNIDADES-T6.json
```

**Até à Sala:** a mesma estrada da §3, com `--rodadas=$A/pesquisadores-conteudo/openalex`. O
`pousar_na_sala.py` só copia `openalex-*.json`; os `autores-orcid-*` ficam de fora.
- ⚠️ **Antes**, o balcão `data/colheita/pesquisadores-t6/rodadas/` da árvore tem de ficar só com as
  páginas novas. O executor lê a pasta **inteira**.
- Se as 589 da 1.ª passagem ainda lá estiverem, o **bruto ganha outras 589 observações**. A Sala não
  duplica, mas o bruto duplica.
- Mover as antigas para um arquivo, sem apagar. Ou pôr no executor uma pasta por corrida (isso é código
  do ramo `t6-para-sala-v1`, não deste).

## 2 · Grupos e laboratórios com feed (`grupos_feeds.py`)

**Sementes** (o endereço lê-se na fila pelo `CANDIDATA_ID`, nada se inventa), por ordem de quantos
pesquisadores nossos estão na casa:
- CREA-DC 64, FEM 61, CNR ×4 (40, **fechado**), Laimburg 13;
- Pisa 8, Torino 6, Milano 6, Padova 5, Marche 5, Napoli 3, Bologna 2, Verona 2, Catania 1, Palermo 1;
- Firenze, Perugia, Foggia, Sassari, Tuscia, Reggio Calabria e Bolzano, todas com 0.

São 24 sementes em 21 domínios.

**Sem semente, porque nenhum livro nosso tem o endereço:**
- **Bari** (DiSSPA), com 5 prioritários;
- **Cattolica** (Fedele, Caffi…);
- **CNR IPSP**.

Isto fica **NÃO SEI**: o endereço não foi inventado.

**De cada página:**
- o **feed declarado**: `<link rel="alternate" type="application/rss+xml|atom+xml">` ou uma ligação que se
  diz RSS/feed;
- os canais públicos (LinkedIn `/in/` fica fora; e-mail e telefone, nunca);
- os **sobrenomes dos nossos pesquisadores daquela casa** que a página escreve. Isto liga o grupo à
  pessoa, sem fundir.

**Os limites:**
- 2 níveis a partir da semente, só dentro do mesmo domínio;
- robots respeitado;
- 5 por domínio por rodada **e** por 24 h;
- CNR só com `--cnr-liberado`.

⚠️ **FEM e CREA partilham os 5 pedidos por 24 h** com as listas oficiais (`listas_oficiais.py`,
PESQ-FORA-DO-MUR): o contador é o mesmo. No mesmo dia é uma **ou** a outra.

**Candidatas** (numa cópia da fila, pela porta canónica):
- um grupo com feed vira CIENCIA, com `FEED_DECLARADO=` e `PESQUISADORES_CITADOS=` na nota;
- cada canal do grupo vira uma candidata do seu tipo.

```bash
A=C:/Users/London1/sintonia-sala-italia
py ferramentas/seguir_pesquisadores/grupos_feeds.py --plano --fila=candidatas/FONTES-CANDIDATAS.json \
   --pessoas=$A/seguir-pesquisadores/PESSOAS-ORDENADAS.json --fora=$A/seguir-pesquisadores/FORA-DO-MUR.json \
   --saida=$A/pesquisadores-conteudo/grupos             # JA FEITO: 24 sementes, 21 dominios
py ferramentas/seguir_pesquisadores/grupos_feeds.py --rodada --autorizado --saida=$A/pesquisadores-conteudo/grupos
py ferramentas/seguir_pesquisadores/grupos_feeds.py --candidatar --saida=$A/pesquisadores-conteudo/grupos --fila=<COPIA da fila>
```

- Uma rodada pode tocar os 21 domínios, até 5 em cada. Isso dá **≤ ~100 pedidos** no total, 3 s entre
  pedidos: cerca de 5 minutos.
- A D90 manda **uma linha de rede de cada vez**: não correr junto com a do OpenAlex.

## 3 · Os 100 estudos T6: o que falta para entrarem na Sala

**O que já está feito:**
- `T6-PARA-SALA.md` §6.2 e a `FILA-PESADO` item 1: o ensaio correu numa cópia da Sala, das 22:03 às
  22:20, com a LOCK-PESADO solta às 22:25.
- Resultado: **104 → 204** (+100 T5, fonte `EU-T5-001`); 2.ª passagem **+0**; `raw_asset` +589 por corrida.

**O que falta, por ordem:**
1. **Decisão do dono** (`T6-PARA-SALA.md` §7). Entram como **T5**, pela régua de ciência que já existe
   (100 dos 589), ou com uma régua T6 própria (sem ela entram 0)? Ou com «o DOI conta como palavra de
   ciência» (345)? E ele autoriza o executor `pesquisadores-t6` à frente na receita T6?
2. **Instalar** `t6-para-sala-v1` no vivo. Já está rebaseado sobre `554c1ec1`, e é o coordenador quem
   instala.
3. **Backup** da Sala (`backup_sala.cmd`).
4. **Correr uma vez** o comando do `T6-PARA-SALA.md` §6.2, com `--universo=T5`. Espera-se **104 → 204**.
5. **Não falta rede nem código.**
   - O que o T6 sabe (pesquisadores, cultura, problema, molécula, local, período) fica no **bruto
     ligado**, não na linha da Sala. Pô-lo na linha é mudar o esquema, e não está pedido.
   - Os materiais novos (§1) seguem a mesma estrada depois disto, com o aviso do balcão.

## 4 · Testes e mutação

- `tests/test_pesquisadores_conteudo.py`: **6** testes.
- Com os anteriores (`test_orcid_lote`, `test_listas_oficiais`, `test_seguir_pesquisadores`) são
  **39 verdes**.
- Mutação: **15/16** mortos. Os testados:
  - ambíguo fora (os dois lados);
  - o teto da rodada do OpenAlex;
  - o cursor;
  - o nome do executor;
  - a medida do resumo;
  - a rede sem autorização;
  - o OpenAlex sem teto de 24 h;
  - o CNR fechado;
  - não seguir outra casa;
  - o feed não adivinhado e o feed do `<head>`;
  - o LinkedIn perfil fora;
  - só citar alvos;
  - o e-mail fora.
- O **sobrevivente** é **equivalente**: tirar o teto da rodada nas páginas de grupo não muda nada, porque
  o contador de 24 h, com 5, para no mesmo sítio.
- Os testes **não saem à rede**: `_urllib` e `portao` estão trocados no módulo de teste (a guarda de 26/09).

## 5 · O que isto não prova

- Nenhuma página real de grupo nem nenhuma obra nova foi vista: sem rede. A contagem de obras e a de
  feeds são **NÃO SEI**.
- As instituições do OpenAlex **erram** («Cereal Research Centre», «Bitron»). A «instituição atual» é a
  do índice.
- Um pesquisador **citado** numa página de grupo é o sobrenome na página, não uma identidade provada.
