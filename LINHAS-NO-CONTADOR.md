# LINHAS-NO-CONTADOR — BUSCA, CIÊNCIA e SOCIAL no mesmo contador da linha SITES

D86 (coleta 24 h) · D90-1/2 (um contador de teto para TODAS as linhas) · D124 (teto adaptativo).
Base: produção `origin/servico-20260923-0923` @ `e24139702`. Ramo: `claude/linhas-no-contador-yth7nl`.

## 1 · O que estava medido (produção, ciclo 20, 28/09 08:14) — e reproduzido aqui

O mesmo ciclo a seco, na árvore base, dá as mesmas quatro mensagens da produção
(`provas/linhas_no_contador/CICLO-A-SECO-BASE-e2413970.json`):

| linha | base `e24139702` | porquê (medido nesta missão) |
|---|---|---|
| SITES | A_CORRER | sonda Node (já existia) |
| BUSCA | ESPERA_LIGACAO `SEM_RESERVA_24H` | a ligação media-se pelo **texto** `reserva_24h.reservar(`; a rota de API (`api_oficial.pedir`) pedia sem reservar |
| CIÊNCIA | ESPERA_LIGACAO `SEM_RESERVA_24H` | `pesquisadores_t6` lia o orçamento **antes** mas pedia por `CP._get` sem reservar pedido a pedido |
| SOCIAL | ESPERA_LIGACAO `SEM_RESERVA_24H` | o `scrap_http` já reservava (D124, via `teto_da_onda`), mas o **texto** não estava lá; e o YouTube Data (`youtube_oficial._http`) pedia **sem reservar** — medido pela sonda nova na base: `YOUTUBE_DATA A: 1 pedidos no servidor, 0 reservas no livro` |
| PESQUISADORES | ESPERA_LIGACAO `TRANSPORTE_NAO_EXISTE_NESTA_ARVORE: coleta/seguir.py` | caminho errado (ver §5) |

## 2 · O que mudou

**Uma porta, um livro.** Nenhum contador novo: tudo escreve no livro da cortesia (`coleta/cortesia_adaptativa.py`,
o mesmo trinco `<livro>.trinco`, a mesma política).

- `coleta/reserva_24h.py:82` `pedir(url, fazer, run_id, linha)` — a porta de UM pedido das linhas Python: reserva
  **antes** (`reservar_ou_esperar`: espera curta sim; orçamento esgotado, Retry-After e pausa de 24 h nunca), `fazer()`
  só com `RESERVADO`, e a resposta — ou a falha, com a marca `TIMEOUT` — vai ao livro **depois** (é ali que o 429/503/
  403/Retry-After vira sinal e o recuo acontece). `:65` `dentro_da_porta` impede o abridor do `scrap_http` de reservar
  duas vezes o mesmo pedido (e **não** cobre um salto para outro domínio: esse reserva à parte — testado).
- **CIÊNCIA** `coleta/pesquisadores_t6.py:749` `_get_no_contador` (OpenAlex, Crossref, ORCID nas duas rodadas de rede):
  pela porta; `:777` `ADIADO_ATE` não conta como pedido e pára o domínio; sem livro, **nada sai**.
  `coleta/corpus_pesquisador.py:229` guarda o código e os cabeçalhos da última resposta (para o sinal chegar ao livro).
- **BUSCA** páginas e motores HTML: já iam por `scrap_http` → `teto_da_onda` → livro. API oficial de busca:
  `ferramentas/linha_busca/api_oficial.py:61` pela porta **quando há livro**; sem livro (GitHub Actions, BUSCA-NO-ACTIONS)
  fica como era — o workflow `linha-busca-google.yml` **não foi tocado**.
- **SOCIAL** `coleta/youtube_oficial.py:241` pela porta quando há livro. `coleta/teto_da_onda.py:159/214` passa o URL
  (rota) e o Crawl-delay; `coleta/scrap_http.py:442` lê o Crawl-delay do robots **já lido** (não pede nada) e `:518`
  leva ao livro o pedido reservado que não teve resposta.
- **Ligação por COMPORTAMENTO.** `ferramentas/big_collection/sonda_ligacao_linhas.py` (nova): para cada rota da linha,
  **num processo seu**, contra um servidor em 127.0.0.1 com livro e política temporários: **A** cada pedido que chegou
  tem RESERVA escrita antes e RESPOSTA depois; **B** domínio PAUSADO → 0 pedidos; **S** o servidor responde 429 → os
  429 ficam no livro como sinal e a 3.ª chamada não sai. Um processo por rota porque, medido, o `scrap_http` instala o
  abridor para o processo inteiro e “ligava” por contágio a rota do YouTube da base.
  `ferramentas/big_collection/coleta_continua.py:100` todas as linhas têm SONDA; `:140` sem sonda **não liga** (o texto
  nunca liga); `:483` linha LIGADA sem executor de ciclo fica **`LIGADA_SEM_ONDA`** com o porquê (a coleta contínua só
  sabe correr `onda_web.py`; correr a onda web com fontes de outra linha seria mentir sobre o executor).

**APIs com limite publicado (D124-3)** — `regras/POLITICA-CORTESIA-ADAPTATIVA.json:40` `REGRA_DO_NUMERO`, `:81` `ROTAS`:

| orçamento | limite publicado 24 h | orçamento | fonte do número |
|---|---|---|---|
| `openalex.org` | 100 000 | 100 000, fixo | docs.openalex.org (CITA) |
| `crossref.org` | **NÃO SEI** (só 5/s publicado) | começa em **5** (mínimo seguro), dobra só sem sinal, teto 432 000 (derivado do ritmo) | crossref.org (CITA) |
| `orcid.org` | **NÃO SEI** (só 24/s publicado) | começa em **5**, idem, teto 2 073 600 (derivado) | info.orcid.org (CITA) |
| `googleapis.com/customsearch` | 100 (acima disso é **pago**) | 100, fixo | developers.google.com + `api_oficial.QUOTA_DIA` |
| `googleapis.com/youtube/search` | 100 chamadas `search.list` | 100, fixo | developers.google.com + `social_matriz.LIMITE_PADRAO_PROJETO` |
| `googleapis.com/youtube` | 10 000 unidades (1 por chamada usada) | 10 000, fixo | idem |
| `googleapis.com` (outra rota) · `brave.com` | **NÃO SEI** | 5, não dobra | — |

A Custom Search e o YouTube Data vivem no **mesmo domínio**; antes eram um orçamento só de 10 000 — cabiam 10 000
buscas pagas. Agora o orçamento é da **rota** (`coleta/cortesia_adaptativa.py:99` `dominio_do_pedido`); o gêmeo Node lê
as classes igual (`coleta/cortesia_adaptativa.mjs:37`, teste de paridade). ⚠️ Todos os números são **de memória,
NÃO CONFERIDOS** nesta missão (proibido visitar sites): o coordenador confere as páginas em `CITA`.

## 3 · Provas

**Ciclo a seco pelo CLI** (`provas/linhas_no_contador/CICLO-A-SECO-DEPOIS.json`, plano de `rodadas.py --so-plano`,
livro vazio, `--max-fontes=5`, 0 rede, 0 Sala):

| linha | estado | motivo exato |
|---|---|---|
| SITES | **A_CORRER** | 5 fontes (IT-T10-018, IT-T10-021, IT-T10-022, IT-T12-024, IT-T12-117) |
| BUSCA | LIGADA_SEM_ONDA | sonda: PÁGINA e API ligadas; a coleta contínua não tem executor de ciclo nem candidatas para ela |
| CIÊNCIA | LIGADA_SEM_ONDA | sonda: API ligada; idem |
| SOCIAL | LIGADA_SEM_ONDA | sonda: SCRAP_HTTP e YOUTUBE_DATA ligadas; idem |
| PESQUISADORES | ESPERA_LIGACAO | `SONDA: SEGUIR A: 2 pedidos no servidor, 0 reservas no livro` |

**D90-2 adversarial** (`tests/test_linhas_no_contador.py:239`): quatro linhas em **quatro processos** — SITES em Node,
CIÊNCIA, BUSCA e SOCIAL em Python — pedem o mesmo domínio no mesmo instante com **1** lugar no orçamento: o servidor
conta **1** pedido, o livro **1** reserva nova, as linhas Python que perderam recebem `ADIADO_ATE ORCAMENTO_ESGOTADO`
sem pedir (3/3 corridas). E, com o orçamento livre e um pedido em voo, a reserva directa da 2.ª linha volta
`ADIADO_ATE UM_DE_CADA_VEZ` e não escreve nada.

**SOCIAL não abre rota** (`:376`): as 37 decisões da `social_matriz` medidas na base
(`tests/fixtures/linhas_no_contador/DECISOES-SOCIAIS-e2413970.json`) são **iguais**, campo a campo, com o livro e
`SINTONIA_LINHA=SOCIAL`; Instagram INCREMENTAL e LinkedIn FETCH_POST continuam `ROUTE_NOT_ALLOWED`; com orçamento livre
um robots `Disallow: /` continua a barrar (só o robots.txt foi pedido).

**portao_real** (`:493`, `ferramentas/big_collection/rodadas.py:332`): `rede.py` com código 3 → `PASSA=False`; código 0
→ `PASSA=True`, e o comando pergunta `--portao-de-egresso IT --sem-cache`; saída ilegível com código 1 → `False`.
O portão continua antes e depois do ciclo (`coleta_continua`: `EGRESSO_ANTES`/`EGRESSO_DEPOIS`, inalterados).

**Mutação** (`provas/linhas_no_contador/mutacao.py`, cópia por `git archive` de `52ab061`, cada mutante só com os
testes que o devem apanhar): **30/30 mortos** (`provas/linhas_no_contador/MUTACAO.json`). Os da missão: linha sem
reserva (M01 porta, M03/M04 CIÊNCIA, M05 BUSCA-API, M06 SOCIAL-YouTube, M07/M08 scrap) · reserva depois do pedido
(M10) · social abre Instagram (M13) e contador por cima do robots (M14) · API acima do limite publicado (M15 CSE,
M16 CSE e YouTube juntos, M17 YouTube, M18 NÃO SEI a começar alto, M19 API publicada a dobrar, M20 gêmeo Node) ·
`portao_real` PASSA fixo (M21) e sem IT (M22). E os da sonda/coleta contínua: texto volta a ligar (M23), sonda sempre
ligada / sem contar reservas / sem ordem / sem B / sem S (M24–M28), linha sem onda entra no ciclo (M29),
PESQUISADORES no caminho errado (M30), porta que tapa outro domínio (M09), resposta/falha não registada (M11/M12).

**Bateria Python por nome** (`provas/int_r7/bateria_por_nome.py`, rede fechada, `git archive` dos dois lados, 3
trabalhadores):

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `e24139702` | 332 | 7507 | 148 |
| 1.ª passagem `43da7cf` | 333 | 7535 | 150 → **2 novas** |
| final `7a1be03` | 333 | 7535 | 148 → **0 novas, 0 sumidas** |

As 2 novas da 1.ª passagem eram testes que afirmavam a premissa antiga, e foram atualizados (declarado abaixo):
`test_lote8_juncoes.test_JL2_busca_existe_e_nao_reserva_fica_a_espera_pelo_motivo_certo` exigia BUSCA em
`ESPERA_LIGACAO SEM_RESERVA_24H` — exatamente o defeito desta missão; `test_t6_para_sala.Consulta2` corria a rede
CIÊNCIA sem livro (agora nada sai sem livro). Os JSON estão em `provas/linhas_no_contador/BATERIA-*.json`.

**Testes mudados (declarado):** `test_coleta_continua.test_ligacao_medida_no_codigo_desta_arvore` esperava as quatro
linhas **desligadas**; agora espera SITES/BUSCA/CIÊNCIA/SOCIAL ligadas pela sonda e PESQUISADORES não, com o porquê.
`test_a_ligacao_e_a_chamada_nao_o_nome` (o texto ligava) virou `test_a_ligacao_e_o_comportamento_nao_o_texto` (o texto
**não** liga) — mais estrito. `test_pesquisadores_t6.RodadaComRedeFalsa` passou a correr com um livro temporário
(sem livro, agora, nada sai — novo teste `test_sem_livro_nenhum_pedido_sai`) e ganhou
`test_cada_pedido_tem_reserva_e_resposta_no_livro`. `test_t6_para_sala.Consulta2` idem (livro temporário).
`test_lote8_juncoes.test_JL2_…_fica_a_espera_pelo_motivo_certo` virou `test_JL2_busca_existe_e_esta_ligada_pela_sonda_nas_duas_rotas`
(BUSCA ligada, com as rotas PÁGINA e API medidas). Nenhuma asserção afrouxada: onde se esperava «desligada», espera-se
agora «ligada», com a medida.

**System Map:** `correr_a_cadeia.py REGERAR` → `VALIDAR` = `SYSTEM_MAP_CHECK=PASS`; `impressao_da_arvore.py
--conferir-carimbo` = IGUAL (medido no commit final; o SHA final vai no relato, porque um commit não sabe o seu SHA).
Depois de `7a1be03` só entraram este relatório, o JSON da bateria e o mapa regerado (nenhum código nem teste).

## 4 · As regras que continuam

Sem login, cookie, CAPTCHA, rota paga (a Custom Search pára nas 100 grátis). robots.txt: o `scrap_http` continua a ler
antes de pedir (a reserva vem **depois** do portão do robots, testado); Crawl-delay entra na pausa mínima. APIs: a
exceção de robots D91 fica como estava. Portão de egresso IT antes e depois, inalterado. Livros vivos
(`curadoria/*-V1.json`, `data/collection-ledger`, `candidatas/FONTES-CANDIDATAS.json`) não tocados.

## 5 · PESQUISADORES — medido, NÃO integrado

`origin/seguir-pesquisadores-v1` (`d0b1d06c`, 26/09) **já é ancestral** da produção: `git merge-base` = a ponta do
ramo. Não há nada para trazer: a produção tem isso e mais 394 commits, incluindo, na mesma pasta
`ferramentas/seguir_pesquisadores/`, `contador.py`, `orcid_lote.py`, `listas_oficiais.py`, `fora_do_mur.py` (+1375
linhas). O `coleta/seguir.py` que a coleta contínua procurava **nunca existiu** — o caminho certo é
`ferramentas/seguir_pesquisadores/seguir.py` (corrigido; agora a sonda mede-o).

Medido pela sonda: `SEGUIR A: 2 pedidos no servidor, 0 reservas no livro` → **ESPERA_LIGACAO**. O que falta:
1. `seguir.Transporte._pedir` usa `contador.py` — **um segundo contador**, ficheiro sem trinco, 5 fixos/24 h, que o
   próprio cabeçalho declara «NÃO é o contador multicanal atómico». Ligá-lo é trocar `Contador24h` pela porta
   (`reserva_24h.pedir`) nas três ferramentas (`seguir`, `orcid_lote`, `listas_oficiais`), que usam `livres()`,
   `proximo_livre()` e o cache de robots de 24 h para planear os dias — uma reescrita com 29 testes à volta, não
   uma ligação;
2. o bloqueio já registado no ramo: o robots.txt real de `pub.orcid.org` é `Disallow: /` → o canário está PARADO;
3. não há executor de ciclo para a linha (como as outras três).
Integrar às cegas trocaria um contador por outro sem medir o planeamento em dias. Fica para missão própria.

## 6 · Instalar (coordenador) — fast-forward sobre `e24139702`

```bat
cd /d %USERPROFILE%\orca\workspaces\eame-sintonia\source-curator-service-v1
set O=%USERPROFILE%\sintonia-sala-italia\ondas
set SI=%USERPROFILE%\sintonia-sala-italia
type nul > %O%\COLETA-CONTINUA\PARAR-COLETA.flag
rem esperar o ciclo em curso acabar (sem COLETA-CONTINUA.trinco em %O%\COLETA-CONTINUA)
git rev-parse HEAD                                   & rem tem de dar e24139702b8216ad54127cf63a14b550bcd4aeab
git fetch origin claude/linhas-no-contador-yth7nl
git merge --ff-only <SHA final do relato>
py -m unittest tests.test_linhas_no_contador tests.test_coleta_continua tests.test_pesquisadores_t6
py ferramentas\big_collection\sonda_ligacao_linhas.py --linha=CIENCIA   & rem tem de dizer "LIGADA": true
py ferramentas\big_collection\coleta_continua.py --ensaio-a-seco --base=%O%\COLETA-CONTINUA ^
   --plano=%O%\ONDA4-RODADAS\RODADAS-PLANO.json --estado-rodadas=%O%\ONDA4-RODADAS\RODADAS-ESTADO.json ^
   --livros-do-dia=%O% --teto-24h=%SI%\TETO-24H.json
del %O%\COLETA-CONTINUA\PARAR-COLETA.flag
```
Só `--ff-only`: se o HEAD do vivo não for `e24139702`, parar e perguntar. O `.cmd` da tarefa não muda.
Atenção: `pesquisadores_t6.py --rede` e `--rede2` passam a **exigir** `SINTONIA_CORTESIA_LIVRO` (sem livro nada sai).

| | |
|---|---|
| **MEDIDO (aqui, sem internet)** | §3, contra servidores em 127.0.0.1 |
| **PREVISÃO** | que as sondas correm no `cmd.exe` do vivo como aqui (Python 3.11 aqui); que os números das APIs batem com as páginas citadas |
| **NÃO SEI** | os limites diários reais de Crossref, ORCID, Brave (declarados NAO_SEI); o livro vivo `TETO-24H.json` (não lido) |

## EM PALAVRAS SIMPLES

O SINTONIA tem cinco “linhas” que vão buscar coisas à internet, e todas deviam anotar no mesmo caderno antes de bater
à porta de um site, para nunca exagerar. Só a linha dos sites anotava de forma provada; as outras quatro ficavam
paradas porque o robô procurava uma frase no código em vez de ver o que o código faz. Agora há uma porta única para
bater: anota primeiro, só depois pede, e escreve o que o site respondeu — se o site disser “calma”, a linha recua.
O robô testa cada linha fazendo pedidos a um site de mentira no próprio computador. Busca, ciência e redes sociais
passaram no teste; mas o robô ainda não sabe pô-las a trabalhar sozinhas no ciclo, e diz isso claramente. As APIs
do Google, OpenAlex, Crossref e ORCID agora usam o limite que elas próprias publicam (ou o mínimo seguro quando não
se sabe) e a busca do Google pára nas 100 grátis por dia. Nenhuma porta fechada das redes sociais abriu. A linha dos
pesquisadores ainda usa um caderno próprio e fica à espera, com o que falta escrito.
