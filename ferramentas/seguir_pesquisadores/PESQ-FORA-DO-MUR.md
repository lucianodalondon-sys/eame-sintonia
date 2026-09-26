# PESQ-FORA-DO-MUR — pesquisadores da FEM, do CREA e do CNR (fora da lista do MUR)

Ramo `pesq-fora-do-mur-v1`, a partir de `seguir-pesquisadores-v1` (d0b1d06c, aceite) — que por sua vez
parte do **vivo `278cd489`**. **Sem rede** (tudo o que sai à rede é comando para o coordenador).
Vivo e Sala não tocados. **SEM MAPA** (a peça está declarada; a cadeia do mapa não correu).
Saída fora do Git: `C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores/FORA-DO-MUR.json`.

## Em palavras simples

- A lista do MUR só tem **professores de universidade**. Quem trabalha na FEM, no CREA ou no CNR
  **não está lá**. Esta missão encontra essas pessoas **pelos trabalhos** da T6: cada trabalho diz em
  que instituição o autor estava quando o escreveu.
- Resultado: **377 pessoas** de 589 trabalhos: FEM **115**, CREA **103**, CNR **134**, e ainda o
  Laimburg (Tirol do Sul, fora do pedido) **33**. Algumas pessoas contam em duas casas: mudaram de
  emprego (ex.: Velasco, FEM → CREA).
- As 4 pessoas pedidas pelo nome estão **todas** na FEM: **Anfora** e **Ioriatti** (nos 589), e
  **Grassi** e **Tonina** (as obras deles vêm da consulta2, fora dos 589).
- **A lista oficial de pessoal** de cada casa lê-se por **rodadas**: no máximo 5 pedidos por site por
  rodada, e só se abre a página de quem já está no cruzamento, nunca a lista toda.
- ⚠️ **FEM:** o formato das páginas é **NÃO SEI** (nunca visitada). A ferramenta **descobre** a lista a
  partir da página de entrada, pelo texto das ligações. Não inventa endereço.
- ⚠️ **CNR:** a coordenação fechou a rede ao CNR (26/09 10:13). A ferramenta **recusa** o CNR sem
  `--cnr-liberado`. E o instituto que mais importa (IPSP, proteção das plantas: **92** das 134 pessoas)
  respondeu **403 e certificado recusado** em 24/09.
- ⚠️ **CREA:** para **82** das 103 pessoas o OpenAlex só diz «Cereal Research Centre», um nome que
  cobre gente de todo o CREA. A instituição é **provável**; o centro é **NÃO SEI**.

## 1 · O cruzamento com os 589 trabalhos (`fora_do_mur.py`)

A casa lê-se no que a **obra** declara (`INSTITUICOES_NESTA_OBRA` do OpenAlex), nunca no nome da pessoa.

| Casa | Pessoas | Unidade certa | Com ORCID | Com obra **recente** (≥2024) e par do casco no texto |
|---|---|---|---|---|
| FEM | 115 | 115 | 86 | 60 (+ 3 pedidas pelo nome sem par recente) |
| CREA | 103 | 36 | 86 | 64 |
| CNR | 134 | 134 (IPSP 92, «CNR sem instituto» 80, IBBR 12, ISPA 11, …) | 112 | 41 |
| Laimburg (extra) | 33 | 29 | 20 | 14 |
| **Total (sem repetir)** | **377** | | **297** | |

Primeiros por casa (obras na T6 / obras recentes com par do casco):
- **FEM:** Anfora 3/1, Ioriatti 5/0, Grassi e Tonina (consulta2: 13 e 9 obras), Perazzolli 19/6, Giovannini 10/3.
- **CREA:** Velasco 7/3, Zeraye Mehari Haile 5/2, Perria 5/2, Bregaglio 5/2, Bergamini 4/2.
- **CNR:** Marzachì 24/6, Galetto 16/5, Marika Rossi 12/3, Abbà 10/3, Matić 5/3 (todos IPSP).

Correções medidas nesta missão (não estão escondidas no número):
1. «**Forestry Research Centre**» **não é CREA**: em 24 das 28 obras aparece ao lado do Laimburg (o
   OpenAlex parte o nome «Laimburg Research Centre for Agriculture and Forestry»). Passou a Laimburg
   PROVÁVEL. A 1.ª corrida contava-o como CREA: o CREA desceu de 123 para 103.
2. «**Canfora**» não é «Anfora»: o sobrenome pedido tem de ser a palavra **inteira**.
3. Há obras em que a instituição vem como **texto** e não como ficha: lêem-se as duas formas.

O que o cruzamento **não** resolve:
- **3 pessoas** têm dois códigos no OpenAlex (Zeraye Mehari Haile, Mickael Malnoy, Urban Spitaler). **Não
  se fundem aqui** (UNKNOWN não funde).
- **4** chaves «sobrenome + inicial» repetem-se dentro da mesma casa (**8 pessoas**). Na lista oficial,
  essas ligações ficam **ambíguas** e **não se abrem**. Isto é perda aceite, não erro.
- Quem não publicou sobre o casco na T6 **não aparece**: a T6 só olhou as culturas e pragas do casco.

## 2 · As listas oficiais: como são as páginas e o que se lê sem login

| Casa | Onde começa (endereço já nos nossos livros) | Formato do perfil | Sem login? | De onde se sabe |
|---|---|---|---|---|
| **FEM** | `www.fmach.it/` (entrada) | **NÃO SEI** | NÃO SEI | ninguém visitou (a P5 listou a FEM e não a visitou: VPN fora, 24/09) |
| **CREA** | 6 páginas de centro: `web/difesa-e-certificazione`, `web/viticoltura-e-enologia`, `web/olivicoltura-frutticoltura-e-agrumicoltura`, `web/agricoltura-e-ambiente`, `cerealicoltura-e-colture-industriali`, `orticoltura-e-florovivaismo` | `crea.gov.it/web/<centro>/-/<nome>`, com campo LinkedIn | **sim** (P4 leu 96 perfis) | P4, 23/09 — os perfis **não** estão no sitemap; só se ligam das páginas dos centros. NÃO SEI em que sub-página do centro fica a lista |
| **CNR IPSP** | `www.ipsp.cnr.it/` | NÃO SEI | **403 + certificado recusado** | P5, 24/09 |
| **CNR IBBR** | `www.ibbr.cnr.it/ibbr/` | `/ibbr/info/people/<nome>` (~160 pessoas) | sim | P5 |
| **CNR ISAFOM** | `www.isafom.cnr.it/` | 91 pessoas; formato do perfil NÃO SEI | sim | P5 |
| **CNR ISPA** | `www.ispa.cnr.it/` | 0 perfis sociais achados | sim | P4/P5 |
| **CNR IBBA** | `ibba.cnr.it/staff-ibba/` | `/staff/<nome>/` com «Linkedin:» | sim | P5 (a IBBA não aparece no cruzamento: nenhuma obra do casco) |

O que se tira de um perfil: só o papel que a própria página escreve e os **links públicos**
(YouTube, X, Bluesky, Mastodon, podcast, blog, **post** do LinkedIn). O perfil pessoal do LinkedIn
(`/in/`) é anotado como **não entra** (muro de login). ResearchGate e Scholar ficam fora. **E-mail,
telefone e contactos nunca.**

## 3 · A ferramenta (`listas_oficiais.py`)

- Usa o mesmo transporte da `seguir.py`:
  - **5 pedidos por domínio por rodada E por 24 h** (D90: o `contador.py` partilhado com o ORCID), contando o
    `robots.txt` (guardado 24 h: o 2.º dia não o relê);
  - robots respeitado; se não se consegue ler, não se pede;
  - 3 s entre pedidos;
  - bytes guardados com sha256 fora do Git;
  - portão IT antes e depois da rodada.
- ⚠️ `ipsp.cnr.it`, `ibbr.cnr.it` e os outros institutos são **o mesmo domínio** (`cnr.it`): dividem os
  5 pedidos da rodada.
- Uma **fila por casa** (`ESTADO-<CASA>.json`): o que não coube na rodada fica para a próxima, e nada se
  pede duas vezes.
- Da página de entrada, segue só as ligações cujo **texto** diz «persone», «personale», «staff»… (e
  essas páginas contam como listas).
- De uma lista, abre só o perfil cujo texto tem o **sobrenome + inicial de um alvo**. Dois alvos
  possíveis = não se abre.
- Ordem: listas primeiro; depois os pedidos pelo nome; depois quem tem mais obra recente do casco.
- `--so-casco`: só quem tem obra **recente** com par do casco, mais os pedidos pelo nome. Dá **FEM 63,
  CREA 64, CNR 41** perfis, no máximo ~16, ~16 e ~11 rodadas de perfis. Com o teto de 24 h (D90), **uma rodada por
  casa por dia**: ~16–18 dias para a FEM e para o CREA (que correm no mesmo dia, domínios diferentes) e
  ~11+ para o CNR (todos os institutos em `cnr.it`).
  - Sem esta opção: 115, 103 e 134 perfis.
- Candidatas: `--candidatar` numa **cópia** da fila, pela porta canónica (`candidatas/fonte_nova.py`),
  com `PAIS=IT` provado pela instituição da pessoa e a página oficial como prova na `NOTA`.

## 4 · Os comandos (o coordenador; VPN IT; uma rodada de cada vez; **uma por casa por dia** — o contador recusa a 2.ª no mesmo dia)

```bash
A=C:/Users/London1/sintonia-sala-italia/seguir-pesquisadores
# o plano (sem rede)
py ferramentas/seguir_pesquisadores/listas_oficiais.py --plano --alvos=$A/FORA-DO-MUR.json
# FEM — 1.a rodada = descobrir a lista (robots + entrada + a lista + 2 perfis); repetir ate NA_FILA=0
py ferramentas/seguir_pesquisadores/listas_oficiais.py --rodada --autorizado --so-casco --casa=FEM \
   --alvos=$A/FORA-DO-MUR.json --saida=$A/LISTAS
# CREA — as 6 paginas de centro primeiro (2 rodadas), depois os perfis
py ferramentas/seguir_pesquisadores/listas_oficiais.py --rodada --autorizado --so-casco --casa=CREA \
   --alvos=$A/FORA-DO-MUR.json --saida=$A/LISTAS
# CNR — SO depois de a coordenacao liberar o CNR (hoje: fechado, 10:13)
py ferramentas/seguir_pesquisadores/listas_oficiais.py --rodada --autorizado --cnr-liberado --so-casco --casa=CNR \
   --alvos=$A/FORA-DO-MUR.json --saida=$A/LISTAS
# as candidatas, numa COPIA da fila (a aplicacao no vivo e do coordenador)
py ferramentas/seguir_pesquisadores/listas_oficiais.py --candidatar --saida=$A/LISTAS --fila=<copia de candidatas/FONTES-CANDIDATAS.json>
```

Cada rodada escreve:
- `RODADA-<CASA>-NN/PEDIDOS.json`: cada pedido e o total por domínio;
- `PORTAO-ANTES.txt` e `PORTAO-DEPOIS.txt`;
- os bytes das páginas.

Se o portão não disser IT, a rodada **para**. FEM e CREA podem correr na mesma volta (domínios
diferentes).

⚠️ **Antes da 1.ª rodada da FEM**, olhar o `ESTADO-FEM.json`. Se a entrada não tiver ligação com
«persone», «staff» ou parecido, a fila fica vazia: a lista da FEM não está na página de entrada, e é
preciso outra pista. Não se deve inventar um endereço.

## 5 · Ensaio sem rede e testes

- **Fixtures:**
  - uma FEM inventada, onde a lista é descoberta na entrada e uma página de «staff» é proibida pelo robots;
  - um CREA com um alvo ambíguo (M. Bianchi) e uma página que falha;
  - um CNR com dois institutos que dividem o teto.
- **Resultado:**
  - `fmach.it` chegou a 5 pedidos: robots + entrada + lista + Tonina + Anfora; Ioriatti ficou para a
    2.ª rodada;
  - a página proibida não foi aberta, e quem não é alvo não foi aberto;
  - o perfil LinkedIn ficou fora; e-mail e telefone foram ignorados;
  - o CNR foi recusado sem liberação, e a rede recusada sem `--autorizado`.
- **Testes:** `tests/test_listas_oficiais.py` **9** + `tests/test_seguir_pesquisadores.py` **9** = 18,
  todos verdes.
- **Mutação:** **8/8** mutantes mortos. Os testados: ambíguo, não-alvo, CNR fechado, LinkedIn perfil,
  pendente do teto, rede sem autorização, ordem, mailto.
  - Dois tinham sobrevivido à 1.ª corrida: o pendente, quando o teto cai no robots do 2.º instituto; e
    o mailto, que era apagado mais à frente. Foram precisos testes novos para os dois.
- **Não testado:** a opção `--so-casco` (é um filtro de uma linha) e o portão real (precisa de rede).

## 6 · Rendimento esperado (honesto)

| Etapa | Esperado | Base |
|---|---|---|
| Perfil oficial com link social, CREA | **baixo**, NÃO SEI o número | P4 leu 96 perfis CREA; os LinkedIn achados eram `/in/` (fora). Posts: NÃO SEI |
| CNR IBBA/ISAFOM | ficha com «Linkedin:» em 37 de 53 (IBBA) — quase todos `/in/`, **fora** | P5 |
| Universidades (comparação) | 0 em 146 páginas de docente fora da Unimi | P5 |
| FEM | **NÃO SEI** | nunca visitada |

Resumo: esta rota prova sobretudo **identidade e papel** (quem trabalha onde, hoje). Canal social que
possa entrar no robô será **raro**, porque o perfil pessoal do LinkedIn fica fora por regra. O que
entrar segue a mesma estrada da `SEGUIR-PESQUISADORES.md` §5:
- YouTube flui;
- post do LinkedIn para no QUALIFY;
- X, Bluesky e podcast vão como site e devem reprovar no canário.

## 7 · O que isto não prova

- Nenhuma página real foi vista nesta missão: sem rede. Os formatos vêm da P4/P5 (23–24/09) e podem ter mudado.
- A casa de cada pessoa é a da **obra**, não a de hoje. Quem mudou de emprego aparece em duas casas; é
  a lista oficial que dirá onde está hoje.
