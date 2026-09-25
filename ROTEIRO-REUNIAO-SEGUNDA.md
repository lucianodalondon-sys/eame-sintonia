# ROTEIRO DA REUNIÃO DE SEGUNDA — SINTONIA EAME (10 minutos)

Missão ROTEIRO-REUNIAO · 25/09/2026 · **só leitura**. Base: `origin/servico-20260923-0923 @ e5cd691f`
(PACOTE-TEMPO-LUGAR instalado no vivo; migração 033 aplicada na Sala real).
Nada no vivo foi tocado. Na Sala só correu `SELECT`, numa sessão com
`default_transaction_read_only = on` (a saída mostrou `on`).

Fontes: `C:/Users/London1/auditoria-madrugada/HANDOFF-VIVO.md` (entradas de 25/09: linhas 325, 328,
338, 339, 342, 345, 384, 387, 388, 390) · `DECISOES-DONO-2026-09-23.md` ·
`TRAVA-POS-ONDA2.md @ 06e5cc18` (página «PARA A REUNIÃO») · medição própria do site público e da Sala.

Estados: **MEDIDO** = medi eu hoje · **DO HANDOFF** = escrito pelo coordenador, conferido no texto,
não re-medido · **NÃO SEI**.

---

## 0. A regra da apresentação: duas caixas

Tudo o que aparece na tela cai numa de duas caixas. Dizer sempre em voz alta qual.

| | FOTOGRAFIA ANTIGA | DE HOJE |
|---|---|---|
| O que é | o portal público | a coleta real e a Sala |
| Datas dos dados | pacote V2.1 de **02/09** + «snapshot da reunião» com corte **07/09 19:23** | ondas de **25/09**, data/local instalados às 17:10 |
| Onde está | `https://sintonia-eame-preview.vercel.app` — publicado em **14/09**, commit `27b9e674` (MEDIDO 25/09 12:21) | banco da Sala (`sala_de_espera_atual`) + livros da coleta. **Sem tela.** |
| Mostra Intelligence? | **sim**: oportunidades e sinais calculados antes da trava | **não**: trava D33 fechada (D57) |

Frase de abertura: *«O portal que vão ver é uma fotografia de 2 a 7 de setembro. O que aconteceu hoje ainda
não tem tela; vou mostrar os números diretamente no banco.»*

---

## 1. Minuto a minuto

### Min 0–1 · Abertura (FOTOGRAFIA ANTIGA)
- Abrir o site → entra sozinho em `accesso` → entrar → `portale`. MEDIDO: abre sem erro.
- ⚠️ A primeira tela é o **Radar delle Opportunità** («AGIRE ORA 6»). É Intelligence de 07/09.
  Não ler esses números. Clicar logo em **Portafoglio**.

### Min 1–3 · O que o portal tem com fonte (FOTOGRAFIA ANTIGA)
- **Portafoglio (173)** → **Label Intelligence (166)**: rótulo oficial, o que foi achado e o que não foi.
- **Concorrenza (577)**, **Polso di Mercato (157)**: observado, com fonte.
- NÃO abrir: Radar delle Opportunità e Radar Futuro (misturam casos de apresentação; são Intelligence);
  Rete Commerciale (18 mensagens inventadas, marcada «demo»).

### Min 3–5 · A coleta de hoje (DE HOJE)

| corrida (25/09) | fontes | resultado | entraram na Sala | Sala |
|---|---:|---|---:|---|
| MICRO-V3, 08:03–08:08 | 6 | 6/6 correram · **2 SIM** / 8 NÃO / 6 NÃO SEI (16 documentos) = 33,3 % → passou o portão (> 16,7 %) | 2 (myfruit) | 69 → 71 |
| 2.ª onda web, 08:12–08:25 | 28 | 20 correram · 7 adiadas pelo teto de 5 pedidos por site · 1 falhou · **7 SIM** / 13 NÃO / 13 NÃO SEI | 7: institutos de pesquisa — **ENEA 3, CREA 2, CNR 1**, e **ARPA Marche 1** | 71 → 78 |

- DO HANDOFF (linhas 325, 328). A 2.ª onda foi **aprovada pelo dono (D60)**, com 1 NÃO SEI definitivo:
  a fonte IT-T2-050 falhou sem deixar linha no livro.
- ⚠️ A `TRAVA-POS-ONDA2.md` conta a mesma onda como **19 correram / 8 adiadas**. NÃO SEI qual está certa.
- Frase: *«Hoje a máquina foi a 34 fontes e pôs 9 documentos novos na sala de espera. A maior parte veio
  de institutos de pesquisa.»*

### Min 5–7 · Data e lugar, instalados hoje (DE HOJE) — **mostrar ao vivo (§2)**
- Prioridade do dono (D61): antes de coletar mais, saber **de quando** e **de onde** é cada coisa.
- Às 17:10 instalado o PACOTE-TEMPO-LUGAR (`e5cd691f`, D74). A migração 033 pôs na Sala um
  **caderno de revisões que só acrescenta**: o original fica intacto; cada correção é uma linha nova;
  o banco **recusa** apagar ou alterar uma revisão.
- Hoje, nos **78** itens da Sala (MEDIDO por SELECT):

| pergunta | itens com resposta | ainda «NÃO SEI» |
|---|---:|---:|
| quando foi publicado | **36 / 78** | 42 |
| onde fica a fonte | **5 / 78** | 73 |
| quando foi o fato | **18 / 78** | 60 |
| onde foi o fato | **13 / 78** | 65 |

- Revisões no caderno: **478** (MEDIDO: 85 local do fato · 85 completude · 85 evidência ·
  80 data do fato · 78 local da fonte · 65 publicação). ⚠️ O coordenador passou **468**; o HANDOFF dá
  455 (1.ª passada) **+23** (2.ª rodada) = **478**, que é o que o banco devolve.
- Frase: *«De manhã eram zero em 78. Agora sabemos a data de publicação de 36 e o lugar do fato de 13.
  Onde não há prova continua escrito "não sei" — nada é inventado.»*

### Min 7–9 · A trava da Intelligence e o que falta (DE HOJE)
- **14 pontos. Hoje: 4 cumpridos · 8 não · 2 sem medidor** (`TRAVA-POS-ONDA2.md @ 06e5cc18`).
  As ondas de hoje **não mudaram nenhum ponto**: o registo delas está fora do Git; o formato não grava
  bruto (RAW) nem derivado por fonte; e os outros pontos medem código, não corridas.
- O que falta, em frases curtas:

| | ponto | hoje |
|---|---|---|
| A | cada fonte italiana com caminho provado ou bloqueio escrito | não — 716 fontes: 98 provadas, 29 bloqueadas, **589 «não sei»** |
| B | nenhuma fonte depende de programa improvisado | sem medidor |
| C | o bruto (RAW) tem um só dono | não — 4 programas escrevem |
| E | o ponto de retoma tem um só dono | não — 2 |
| G | o dado organizado tem dono por tipo | não — só há documentos inteiros |
| H | a escolha do caminho não está espalhada | não — 6 sítios decidem a rota |
| J | o Git não guarda o estado do dia a dia | não — os livros da coleta cresceram hoje |
| K | uma falha não vira «sucesso» falso | sem medidor |
| M | o mapa do sistema mostra tudo | não — 202 de 241 peças sem descrição conferida |
| N | a inteligência continua congelada | não — 21 ficheiros mudaram desde 08/09; 5 são avanço proibido |

  Cumpridos: D (contrato da corrida), F (dono do texto extraído), I (serviço pago não é o caminho
  normal), L («não sei» continua «não sei»).
- ⚠️ Esta contagem é de ~09:15, antes da data/local. NÃO SEI se a 033 muda o ponto G; ninguém re-mediu.
- Frase: *«A inteligência está desligada de propósito. Só liga com os 14 pontos cumpridos.»*

### Min 9–10 · Próxima coleta e fecho
- Caminho (DO HANDOFF, linha 390, números **aproximados**): MICRO de verificação (sem ondas) →
  instalar a 3.ª onda ajustada → congelar a lista (**~60 fontes**) → 3.ª onda (**~36 correm**,
  ~150 pedidos, no máximo 5 por site) → onda social à parte.
- Fecho: *«Hoje a Sala foi de 69 para 78 e ganhou data e lugar. A seguir: mais fontes, e depois fechar
  a trava. Só então o portal passa a mostrar o que é de hoje.»*

---

## 2. Três consultas para mostrar ao vivo (só leitura)

Abrir a sessão **sempre** em modo só leitura. As opções vêm antes da DSN: o `psql` do Windows ignora
as opções que vierem depois dela.

```bash
S=$HOME/sintonia-sala-italia
export PGPASSFILE="$S/pgpass.conf"
export PGOPTIONS="-c default_transaction_read_only=on"
DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
$HOME/orca/pgtmp/pgsql/bin/psql.exe -X -A -F' | ' -f consultas.sql "$DSN"
```

**Consulta 1 — quantos itens, e quantos já têm data e lugar**
```sql
show default_transaction_read_only;   -- tem de dizer: on
select count(*) as itens,
  count(*) filter (where published_at    <> 'NAO SEI') as publicacao,
  count(*) filter (where source_location <> 'NAO SEI') as local_fonte,
  count(*) filter (where fact_time       <> 'NAO SEI') as data_fato,
  count(*) filter (where fact_location   <> 'NAO SEI') as local_fato,
  count(*) filter (where revisoes > 0)                 as com_revisao
from sala_de_espera_atual;
```
Resultado em 25/09, depois das 17:10: `78 | 36 | 5 | 18 | 13 | 78`

**Consulta 2 — o caderno de revisões (só acrescenta)**
```sql
select campo, count(*) as revisoes
from sala_de_espera_revisao group by campo order by 2 desc;
select count(*) as total_revisoes from sala_de_espera_revisao;
```
Resultado: `fact_location 85 · completude_tempo_lugar 85 · tempo_lugar_evidencia 85 · fact_time 80 ·
source_location 78 · published_at 65` · total **478**

**Consulta 3 — cada lugar com a frase que o prova**
```sql
select source_id, left(fact_time,20) as data_fato,
       left(fact_location,30) as local_fato, left(fact_location_basis,160) as prova
from sala_de_espera_atual
where fact_location <> 'NAO SEI' order by source_id limit 13;
```
Mostra 13 linhas. Exemplo real: IT-T10-018 · 2026-09-23 · Firenze · a frase *«Osservatorio Piccoli
Frutti a Firenze che, oggi 23 settembre 2026, …»*.

⚠️ **O que a consulta 3 também mostra, e é preciso dizer antes que perguntem:**
- **IT-T5-015** e **IT-T5-030** aparecem **duas vezes cada**, com o mesmo texto: o mesmo documento
  entrou duas vezes na Sala. É defeito, não enfeite. NÃO SEI a causa; não investiguei.
- **IT-T5-090** traz congressos de **2013 e 2023**: página de arquivo, não notícia de agora.
- **IT-T5-030** é um seminário de cibersegurança em Teramo: tem data e lugar certos, mas **não é agro**.
- Frase: *«O sistema agora diz de onde tirou cada data e cada lugar. Por isso também vemos o que ainda
  está errado.»*

---

## 3. O que NÃO dizer

- Nada de «oportunidade», «sinal» ou «agir agora» sobre dados de hoje: não existe; a trava está fechada.
- Os números do Radar (17 / 43 / 6) são da fotografia de 07/09, não de hoje.
- O portal **não lê** a Sala; as revisões não aparecem em nenhuma tela.
- «78 com data»: não. São 36 com data de publicação e 18 com data do fato.

## 4. Plano B sem internet

1. Portal: cópia da `e5cd691f` **fora do repositório** e `py security/servir_como_a_vercel.py 8931` →
   `http://127.0.0.1:8931/`. MEDIDO com a `df0865e6`: o caminho index → accesso → portale abre. Entre as
   duas versões, as páginas do portal são iguais; só o System Map mudou.
   Ressalva: o mapa da Europa na entrada vem de uma CDN (site de terceiros); sem internet pode não
   aparecer. NÃO PROVADO.
2. As 3 consultas usam a Sala **local**; não precisam de internet.
3. Levar em PDF ou print: as tabelas das secções 1 e 2 e a página «PARA A REUNIÃO».

## 5. Antes de segunda, re-medir (só leitura)

| # | o quê | por quê |
|---|---|---|
| 1 | consulta 1 | a MICRO de verificação pode ter posto mais itens na Sala (o robô está ligado) |
| 2 | 2.ª onda: 20 ou 19 correram | o HANDOFF e a TRAVA não batem |
| 3 | 468 ou 478 revisões | o banco devolveu 478 às ~18h de 25/09 |
| 4 | site público ainda é `27b9e674` | se alguém publicar a linha nova, a página `/casa` volta a ficar pública |
| 5 | pontos da trava depois da 033 | a contagem 4/8/2 é de antes da data/local |
