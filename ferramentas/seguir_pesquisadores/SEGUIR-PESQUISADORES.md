# SEGUIR-PESQUISADORES (D85) — quem seguir, onde procurar, e quanto se deve esperar

Ramo `seguir-pesquisadores-v1`, a partir do **vivo `278cd489`**. **Sem rede** (tudo o que sai à rede é
um comando para o coordenador correr). Vivo e Sala não tocados. **SEM MAPA.**
Saída fora do Git: `C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores/`.

## Em palavras simples

- **Quem:** da lista oficial do MUR (278 docentes de patologia e entomologia), **124** ficam ligados,
  com segurança, a trabalhos da T6 sobre as culturas e pragas do casco. A regra: mesmo sobrenome +
  mesma inicial + **mesma universidade**. Nome sozinho não liga pessoa nenhuma.
  - **5** ficam ambíguos e **4** têm o nome igual mas estão em outra universidade: nenhum desses se funde;
  - **146** não têm obra na T6 (o que não quer dizer que não publiquem: a T6 só olhou o casco).
- **Por onde começar:** os **60** com mais trabalhos **recentes** (2024 em diante) com par
  cultura×praga do casco **confirmado no texto**, mais os 3 pedidos pelo nome (Zappalà, Tonina,
  Grassi) = **63**. Entre os primeiros: Fedele e Caffi (Cattolica), Cotrozzi (Pisa), **Toffolatti**
  (Milão), Duso (Pádua), Domenico **Bosco** (Turim). ⚠️ A T6 foi montada a partir das consultas do
  casco, com muita videira: a ordem pende para a vinha.
- **Como se segue cada pessoa:**
  1. o ORCID dela, lendo **só** os links que a própria pessoa declarou;
  2. a página da universidade ou do laboratório que ela declarou, e dali os links para YouTube, X,
     Bluesky, podcast, blog e **post** do LinkedIn.

  O perfil pessoal do LinkedIn fica **fora** (pede login). E-mail, telefone, seguidores e contatos
  **nunca** se guardam.
- **Limites dentro do código:** 5 pedidos por domínio por rodada (contando o robots), robots
  respeitado, 3 s entre pedidos, portão IT antes e depois. Os bytes de cada página ficam guardados
  com sha256, fora do Git.
- **Ensaio sem rede:** com 7 pessoas inventadas, as regras funcionaram, e **6 de 6** estragos feitos
  de propósito foram pegos pelos testes. As candidatas entraram pela porta oficial numa **cópia** da
  fila (13 novas); a fila do robô de verdade ficou igual (sha256 antes = depois).
- ⚠️ **Rendimento esperado, honesto: baixo pelo ORCID.** A única medida real que existe: **2 de 13**
  pesquisadores declaravam links no ORCID, e **0 dos 3 italianos**. Dos 63, espera-se que só **alguns**
  revelem canais por aqui. O caminho que mais vai render — a **página oficial do docente** no site de
  cada universidade — **não está feito**: cada universidade tem um formato, e isso precisa de ser
  medido (os 63 estão em 19 universidades; Pisa 8, Milão 6, Turim 6, Pádua 5, Marche 5, Bari 5…).
- ⚠️ **E hoje o robô de fontes só sabe levar até ao fim dois tipos:** canal do **YouTube** (pela rota do
  Scrap) e **página** (HTML). Post do LinkedIn de pessoa **pára** no QUALIFY; X, Bluesky, Mastodon e podcast
  seguem como «site comum» e devem **reprovar** no canário — por falta de rota própria (ver §5). Isso não se esconde: fica escrito em
  cada candidata.

## 1 · Quem seguir (`pessoas.py` → `PESSOAS-ORDENADAS.json`, sha256 `ac29a656fe4355b7…`)

| Ligação | N | O que quer dizer |
|---|---|---|
| NOME+UNIVERSIDADE | 124 | identidade oficial MUR ligada a obra T6 (sobrenome + inicial + mesma universidade) |
| SEM_OBRA_NA_T6 | 146 | identidade oficial; a T6 não tem obra do casco desta pessoa |
| AMBIGUO | 5 | dois autores T6 servem; não se funde |
| SO_NOME_OUTRA_UNIVERSIDADE | 4 | nome igual, universidade diferente: homónimo possível; não se liga |
| consulta2 | 5 | Zappalà, Tonina, Grassi RESOLVIDOS; Biondi AMBIGUO (2 ORCID); «Daniele» Bosco não existe (é Domenico, já no MUR) |

**Prioridade = 63**: os 60 primeiros por (obras recentes com par do casco no texto → obras com par →
obras recentes → tem ORCID) + os 3 da consulta2 resolvidos. Todos os 60 têm **um** ORCID; Grassi não tem
nenhum (não se segue: sem identidade única no ORCID). SSD: AGRI-05/B (patologia) 43, AGRI-05/A
(entomologia) 17. Cada pessoa leva o **porquê** (as obras e os pares) no JSON. A contagem de obras
decide só por quem se começa — não é nota de importância (skill D85).

## 2 · A ferramenta (`seguir.py`)

| Pedido | Domínio | Quantos |
|---|---|---|
| `robots.txt` do host | cada host | 1 por host por rodada (conta no teto) |
| ORCID `researcher-urls` (a secção **mínima**: só os links declarados; nunca `/person` nem `/email`) | `orcid.org` | 1 por pessoa; **4 pessoas por rodada** (robots + 4 = 5) |
| Página declarada no ORCID (institucional/pessoal/laboratório) | o da universidade | até 2 por pessoa; teto 5 por domínio |
| Perfis sociais | — | **nenhum**: o endereço basta; quem os abre é o robô (QUALIFY → contrato → rota → canário) |

Classificação: LinkedIn `/in/` → **fora** (muro de login); `/posts/`, `/feed/update/` → LINKEDIN;
YouTube → YOUTUBE; X, Bluesky, Mastodon, podcast → OUTRO; blog/newsletter → IMPRENSA; página → CIENCIA;
ResearchGate e Google Scholar → fora (muro / índice, não canal do dia a dia). E-mails e telefones da
página são ignorados.

Quem não coube no teto de uma rodada fica `PENDENTE` com o motivo (não é falha). ⚠️ A ferramenta ainda
**não relança sozinha** os pendentes: a próxima rodada é outro grupo de 4 pessoas.

## 3 · Os comandos (o coordenador; VPN IT; uma rodada de cada vez)

```bash
# o plano (sem rede): 16 rodadas, 4 pessoas cada (a 16.a: Zappalà, Tonina, Grassi)
py ferramentas/seguir_pesquisadores/seguir.py --plano --so-prioridade \
   --pessoas=C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores/PESSOAS-ORDENADAS.json
# rodada N (sai à rede; portão IT antes e depois, e pára se não for IT)
py ferramentas/seguir_pesquisadores/seguir.py --rodada=N --autorizado \
   --pessoas=C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores/PESSOAS-ORDENADAS.json \
   --saida=C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores
# as candidatas, pela porta canónica, numa CÓPIA da fila (a aplicação no vivo é do coordenador)
py ferramentas/seguir_pesquisadores/seguir.py --candidatar \
   --saida=C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores --fila=<cópia de candidatas/FONTES-CANDIDATAS.json>
```

Uma rodada: ≤ 5 pedidos a `orcid.org`, ≤ 5 a cada universidade, 3 s entre pedidos (~1 min).
`PLANO-RODADAS.txt` (fora do Git) tem as 16 rodadas com os nomes.

## 4 · O ensaio offline (`fixtures/`, `tests/test_seguir_pesquisadores.py`)

7 pessoas inventadas: páginas com X, podcast, post e perfil do LinkedIn, ResearchGate, e-mail; um robots
que proíbe; um ORCID que não responde; uma pessoa sem ORCID e outra com dois; páginas demais no mesmo
domínio. Resultado: `orcid.org` 5, `uni-exemplo.it` 5 (teto respeitado); a página proibida não foi aberta;
perfil do LinkedIn e ResearchGate **fora**, post **dentro**; sem ORCID e ORCID duplo **não seguidos**;
o 5.º ORCID ficou `PENDENTE` pelo teto. `--candidatar` numa cópia da fila do vivo: **13** candidatas
(CIENCIA 5, OUTRO 4, YOUTUBE 2, LINKEDIN 1, IMPRENSA 1), com `PARA_QUE` (D85), `PAIS=IT` provado pela
universidade da **pessoa** (nunca o lugar do facto) e a prova na `NOTA`. A fila do vivo: sha256 igual
antes e depois.

Testes: **9**, todos verdes. Mutação: **6/6** (teto, robots, perfil LinkedIn, ORCID ambíguo,
universidade na ligação, e-mail nas ligações). O do ORCID ambíguo sobreviveu à 1.ª corrida — o teste
só olhava os canais —, e foi reforçado: pessoa ambígua não faz **nenhum** pedido.

## 5 · Rendimento esperado (honesto)

| Etapa | Esperado | Base |
|---|---|---|
| Pessoas com identidade + obra do casco | 124 de 278 (MUR AGRI-05) | medido nesta missão |
| Com ORCID único (prioridade) | 62 de 63 | medido |
| Que declaram **algum** link no ORCID | ~15 % → ~9 dos 63 (intervalo largo: 0–20) | **2 de 13** no piloto de speakers (ES/FR); **0 de 3** italianos |
| Que declaram canal **social** no ORCID | ~1 em 13 → ~0–5 dos 63 | 1 de 13 no mesmo piloto (um X) |
| LinkedIn | **só posts**; perfis ficam fora | D24/D85 |
| Página oficial do docente (a rota que mais renderia) | **NÃO SEI** — não feita | precisa de receita por universidade (19) |

O que acontece depois, no robô de fontes (vivo de hoje):
- **YOUTUBE** → contrato da rota do Scrap (SOC2) → canário do Scrap: **flui**;
- **CIENCIA** (página) → contrato HTML → canário: flui, mas página de biografia raramente tem «notícias»;
- **LINKEDIN post de pessoa** → o QUALIFY de hoje só aceita `/company/`: **pára** até a fase
  `video-post-linkedin` da D80 existir;
- **OUTRO** (X, Bluesky, Mastodon, podcast) → sem rota própria: o QUALIFY trata-o como **site comum**
  (`worker.py`: tudo o que não é YOUTUBE/LINKEDIN é `HTML_SITE`), escreve-lhe um contrato de página, e o
  canário deve **reprovar** (o X pede login; perfis de Bluesky/Mastodon não são listagens de notícias;
  podcast: o áudio não se baixa, VOZES-AGRONOMOS). Reprovar ali é o circuito a funcionar, não um erro;
- **IMPRENSA** (blog/newsletter) → como página.

## 6 · O que falta (para o D85 render de verdade)

1. **Receitas da página de docente** das 19 universidades (a mais rentável), medidas em copia: cada uma
   com o seu formato; sem inventar endereço.
2. **Relançar os PENDENTES** do teto numa rodada própria (`--so-pendentes`, não feito).
3. **Rotas** para as contas que hoje param: LinkedIn post (D80), Bluesky (conta), X (NÃO SEI se existe
   rota sem login).
4. **D85.5 — know-how e Bíblias:** não redigido nesta missão (a missão não o pedia); fica por fazer.

## 7 · O que isto não prova

- Nenhum canal real foi visto: sem rede. Os números da §5 vêm de um piloto pequeno (13 pessoas).
- A ligação MUR↔T6 é por nome + inicial + universidade: evita o homónimo óbvio, não o impossível.
