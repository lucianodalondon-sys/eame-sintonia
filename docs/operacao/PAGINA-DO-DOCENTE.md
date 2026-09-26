# PAGINA-DO-DOCENTE — a página oficial de cada docente, universidade a universidade

> Ramo `pagina-docente-v1`, a partir de `seguir-pesquisadores-v1` (d0b1d06c). Missão: coordenação 17:35 (a parte
> que faltava do SEGUIR-PESQUISADORES, §6.1). **Sem rede**: só os bytes que já temos (P5, acervo, ronda 1) e os
> endereços que estão nos nossos livros. Vivo, Sala e fila do robô não foram tocados. **SEM MAPA.**
> Saída fora do Git: `C:/Users/London1/sintonia-sala-italia/pagina-docente/`.

## Em palavras simples

- **Quem:** dos 63 prioritários, **60** estão nas **19 universidades**. Os outros **3** (Zappalà, Tonina, Grassi)
  não têm universidade na lista do MUR. Estão ligados à FEM e a outros institutos, e ficam fora deste caminho.
- **O que já se sabia sem pedir nada:** a missão P5 (24/09) guardou **478 páginas reais de docente** de **5
  universidades**: Milão 165, Palermo 163, Pádua 71, Verona 69 e Údine 10. Foram medidas.
  - **O problema:** em Milão, Palermo, Verona e Údine, **407 de 407** páginas trazem, no cabeçalho e no
    rodapé, as redes sociais **da universidade**. Sem cortar isso, quase todo docente «teria» Facebook e
    Instagram. Cada leitor corta só o **pedaço da página que é da pessoa**. O corte deu certo em **478 de 478**.
  - **O que sobra, dentro do pedaço da pessoa:**
    - **12 de 478** páginas (2,5%) têm algum link para canal ou perfil;
    - **6 de 478** (1,3%) têm um que pode virar candidata: **1 canal do YouTube** e **5 sites pessoais**,
      todos em Milão;
    - Palermo, Pádua e Údine: **0**.
  - **Os perfis que aparecem ficam fora:** ResearchGate, Google Scholar, ORCID e perfil pessoal do LinkedIn
    (este pede login).
- **Dos 60:**
  - **8** já têm a página guardada e foram lidos agora, sem rede: Toffolatti, Maddalena, Quaglino, Bianco,
    Passera, Matic, Vandelle e Polverari. Resultado: **0 canais**. Só um ResearchGate (fica fora) e 1 página
    de «expertise» da universidade, que a rodada abre como segundo passo.
  - **5** já têm o endereço da página achado na lista guardada (Pádua: Duso, Pozzebon, Scaccini, Sella,
    Tundo).
  - **2** não estão nas listas guardadas:
    - Di Francesco (Údine): a lista vem em páginas, e só a 1.ª está guardada;
    - Rigamonti (Milão): é de outro departamento.
  - **45** precisam de rede.
- **Os leitores:** um por universidade, **19**, no ficheiro `universidades.py`. Estão em três graus de certeza:
  - **5 medidos em bytes reais** (Milão, Palermo, Verona, Pádua, Údine). Sabe-se a lista, a forma do endereço
    e onde começa e acaba o pedaço da pessoa;
  - **6 só com a entrada conhecida** (Bolonha, Nápoles, Marche, Teramo, Catânia, Bari). O endereço da lista de
    docentes está num link real que já guardámos;
  - **8 só com a casa do site** (Pisa, Turim, Cattolica, Trento, Molise, Sapienza, Salerno, Unimore). A rodada
    abre a casa e procura nela o link «docenti/persone» (1 pedido a mais).

  ⚠️ Nestes 14 leitores a forma da página **NÃO foi medida**. Eles usam o leitor genérico:
  - tira as contas cujo endereço tem o nome da universidade;
  - tira os links repetidos em várias páginas da mesma universidade.

  É mais fraco do que o corte medido.
- **O comando:** fica pronto para o coordenador correr por rodadas. Os limites estão no código:
  - no máximo 5 pedidos por domínio em cada rodada, contando o `robots.txt`;
  - o robots é respeitado;
  - 3 segundos entre pedidos;
  - o portão IT é conferido antes e depois;
  - e-mail e telefone nunca se guardam.

  Estimativa: **4 rodadas** e mais 1 para os segundos passos.
- **Rendimento esperado, honesto: baixo.** A medida real diz **~1 canal que entra em cada 80 páginas**, e só
  em Milão. É **provável** que, dos 45 ainda por abrir, saiam **0 a 3 canais**. É uma estimativa por semelhança
  com as 5 universidades medidas; as outras 14 podem ser diferentes. O que a página rende mais são as
  **páginas próprias** (laboratório, site pessoal), que a rodada abre como segundo passo.

## 1 · Os 60, por universidade (`--plano`)

| Universidade | Pessoas | Já lida sem rede | Endereço já conhecido | Leitor | Por rodada | Entrada (prova) |
|---|---|---|---|---|---|---|
| Pisa | 8 | 0 | 0 | casa do site | 2 | `agr.unipi.it/` (livro, 104 menções) |
| Milão | 6 | 5 | 0 | **medido** | 3 | `disaa.unimi.it/…/persone` (bytes P5) + regra de endereço |
| Turim | 6 | 0 | 0 | casa do site | 2 | `disafa.unito.it/` (livro) |
| Marche | 5 | 0 | 0 | só entrada | 3 | `univpm.it/…/Docenti-della-facolta-di-Agraria` (link na página P5 do d3a) |
| Pádua | 5 | 0 | **5** | **medido** | 3 | `dafnae`/`tesaf` `…/personale-docente` (bytes P5) |
| Bari | 5 | 0 | 0 | só entrada | 3 | `uniba.it/…/disspa` (livro) |
| Trento | 4 | 0 | 0 | casa do site | 2 | `unitn.it/` (livro) |
| Cattolica | 4 | 0 | 0 | casa do site | 2 | `piacenza.unicatt.it/` (livro) |
| Nápoles | 3 | 0 | 0 | só entrada | 3 | `agraria.unina.it/…/docenti-e-ricercatori` (link na ronda 1, V17) |
| Molise | 3 | 0 | 0 | casa do site | 2 | `unimol.it/` (livro) |
| Bolonha | 2 | 0 | 0 | só entrada | 3 | `distal.unibo.it/…/persone` (link no acervo) |
| Verona | 2 | **2** | 0 | **medido** | 3 | `dbt.univr.it/?ent=persona` (bytes P5) |
| Sapienza, Údine, Unimore, Teramo, Salerno, Palermo, Catânia | 1 cada | Palermo 1 | 0 | ver `universidades.py` | 2–3 | idem |

## 2 · O que cada leitor medido sabe (bytes reais da P5)

| Universidade | Lista | Endereço da pessoa | Pedaço da pessoa (início → fim) | Campo próprio |
|---|---|---|---|---|
| Milão | `disaa…/contatti/persone` | `unimi.it/it/ugov/rubrica/personNNN` | `ugov-rubrica--view-mode-full` → `<footer` | «Sito web» (16 de 165 preenchido) |
| Palermo | `saaf/?pagina=personale&ruolo=docenti` | `unipa.it/persone/docenti/<letra>/<nome.sobrenome>` | `id="content"` → `<footer class="footer"` | — |
| Verona | `dbt.univr.it/?ent=persona` | `dbt.univr.it/?ent=persona&id=N` | `row info-persona` → `id="footer"` | — |
| Pádua | `<dep>.unipd.it/category/ruoli/personale-docente` | `…?key=<32 hex>` | `sideblock personale` → `<!-- footer -->` | — |
| Údine | `di4a…/cercapersone_dept?afferenza=107404` (10 por página) | `…@@cercapersone_detail?person-id=<32 hex>` | `content-core` → `viewlet-below-content-body` | «Sito personale People@uniud» (10 de 10; é da universidade) |

Achados que o leitor precisou de aprender, todos medidos:
- **Údine:** o link da lista diz só «Profilo completo». O nome está no **cartão** do docente, e a lista vem em
  páginas de 10.
- **Milão:** o endereço `…/it/ugov/person/<nome>-<sobrenome>` segue uma regra que bate em **154 de 165** páginas
  reais. Serve para Rigamonti, que não está na lista guardada. A página **só vale se o nome conferir nela**.
- **Bolonha:** `unibo.it/sitoweb/<nome.sobrenome>` tem **1 exemplo** no livro. É uma regra fraca, com a mesma
  trava do nome.

## 3 · O comando (o coordenador; VPN IT; uma rodada de cada vez)

```bash
B=<clone de origin/pagina-docente-v1>
P=C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores/PESSOAS-ORDENADAS.json
M=$B/data/derivados/PAGINA-DOCENTE/MEDIDA-OFFLINE.json
S=C:/Users/London1/sintonia-sala-italia/pagina-docente
py $B/ferramentas/pagina_docente/rodadas.py --plano --pessoas=$P --medida=$M          # sem rede
py $B/ferramentas/pagina_docente/rodadas.py --rodada=1 --autorizado --pessoas=$P --medida=$M --saida=$S
#   portao IT antes (para se nao for IT) -> ~19 dominios, <=5 pedidos cada (robots incluido), 3 s -> portao IT depois
#   rodada 2, 3, ...: o mesmo comando com --rodada=N+1 (a rodada le as anteriores da mesma --saida:
#   o que ficou PENDENTE pelo teto ou FALHA de rede volta primeiro; o que esta feito nao se repete)
#   parar quando a rodada so tiver FALHA (servidor que nao responde) ou nada por fazer
py $B/ferramentas/seguir_pesquisadores/seguir.py --candidatar --saida=$S --fila=<COPIA de candidatas/FONTES-CANDIDATAS.json>
```

- Uma rodada pede **≤ 5 por domínio** (ex.: `unimi.it` = robots de `disaa` + lista + robots de `www` + 2
  páginas). O que não couber fica **PENDENTE** e volta na rodada seguinte.
- **Segundo passo:** a página própria que a página oficial declara é aberta na rodada seguinte, 1 por pessoa.
  Pode ser o campo «Sito web», um site de laboratório ou um site pessoal externo. Dela tiram-se os links para
  YouTube, X, Bluesky e post do LinkedIn. Um canal já registado numa rodada anterior não se repete.
- **A saída** tem o mesmo formato do `seguir.py`. As candidatas entram pela porta canónica numa **cópia** da
  fila. No ensaio: 5 candidatas numa cópia da fila do vivo. A fila do vivo ficou igual: sha256 `772b5564…` antes
  e depois.
- **Ensaio a seco do comando real** (feito): com `HTTP(S)_PROXY=127.0.0.1:9`, o portão deu «não é IT» e o
  comando **PAROU com 0 pedidos** (`pagina-docente/ENSAIO-A-SECO/`).

## 4 · O ensaio offline e os testes

- `fixtures/`: **12 páginas reais** reduzidas a partir dos bytes da P5, com sha256 conferido
  (`ORIGEM-DAS-FIXTURES.json`, `fazer_fixtures.py`). A redução tirou scripts, e-mails e telefones. As listas
  ficaram só com os links. Há também **5 páginas SINTÉTICAS**, marcadas no nome. Elas simulam a casa, a lista,
  a pessoa e o site pessoal de Pisa, mais a 2.ª página de Údine, e **só** testam o caminho. Não são medida.
- **2 rodadas a seco:**

  | O que o ensaio fez | Resultado |
  |---|---|
  | teto | `unimi.it` 5 de 5; o 6.º pedido ficou PENDENTE e voltou na rodada 2 |
  | robots que proíbe | Turim: 1 pedido, só o robots |
  | endereço construído que abre outra pessoa | NOME_NAO_CONFERE, nada lido |
  | lista paginada | Údine: achou na 2.ª página |
  | cabeçalho da universidade | Palermo: 0 canais, apesar de 5 redes da universidade na página |
  | segundo passo | Pisa: X e Bluesky, sem repetir o YouTube |
  | falha de rede | volta na rodada seguinte |
  | e-mail e telefone | nunca na saída |
- **Testes:** `tests/test_pagina_docente.py`, **16**, e `tests/test_seguir_pesquisadores.py`, 9. Todos passam
  (25).
- **Mutação:** 12 de 12 (§6).

## 5 · O que isto não prova

- **14 de 19** leitores não foram medidos: a forma da página dessas universidades é **NÃO SEI** até à 1.ª rodada.
  O leitor genérico pode deixar passar uma conta da universidade cujo endereço não traga o nome dela, ou
  perder um link pessoal sem rótulo. Esses links ficam em `EXTERNOS_SEM_ROTULO`, para leitura humana, e não
  viram canal.
- As páginas da P5 são de **24/09**: podem ter mudado.
- O rendimento da §«Em palavras simples» vem de 5 universidades, e **uma só** (Milão) deu canais.
- Os 3 fora das 19 (FEM e outros) não têm leitor. As páginas da FEM não foram medidas: na P5 só havia o login.

## 6 · Mutação

**12 de 12** estragos feitos de propósito foram pegos pelos testes. A corrida foi numa **cópia** das pastas, fora
da worktree (`ferramentas/pagina_docente/mutar.py.txt`), e a cópia sem estrago voltou verde.

| Estrago | Pego? |
|---|---|
| M1 · sem o corte do pedaço da pessoa | sim |
| M2 · achar só pelo sobrenome | sim |
| M3 · o nome «confere» sempre | sim |
| M4 · sem o filtro das contas da universidade | sim |
| M5 · e-mail no texto do link não é limpo | sim |
| M6 · o cartão de Údine é ignorado | sim |
| M7 · FALHA de rede vira final | sim |
| M8 · um canal repete-se entre rodadas | sim |
| M9 · um curso «Laboratorio di…» conta como página própria | sim |
| M10 · um link de outro domínio serve como página do docente | sim |
| M11 · o PENDENTE pelo teto não volta | sim |
| M12 · uma regra de endereço inventada para Pisa | sim |
