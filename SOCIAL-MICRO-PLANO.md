# SOCIAL-MICRO-PLANO — preparação da MICRO social (25-26/09)

Ramo `social-micro-v1`, a partir do vivo `ce28040c` (3.ª onda + coorte). Por cima, por cherry-pick, os 4 commits
da PROVA-TETO-SOCIAL (`origin/prova-teto-social-v1` @ ff8a7028: 6bd3da95, 9522defb, 8114d3ca, 19593d30) e o
conserto desta missão (817ae906). **Rede FECHADA o tempo todo** (`HTTP(S)_PROXY=127.0.0.1:9`). Nada no vivo, nada
na Sala real, nada instalado. **A micro NÃO foi corrida.**

## CAUSA_0_ITENS

O «0 itens na Sala» tinha **duas causas, e só uma era defeito do produto**:

1. **O meu arnês, não o produto.** A corrida descartável chamava `orquestrador.correr(...)` sem `memoria`,
   `banco_do_rastro` nem `raiz_do_armazem`. Sem eles não há banco ligado: o recibo dizia `STATUS SUCCESS`, e a
   Admissão julgava, mas nada pousava. É a lei §132 do know-how (DEPENDÊNCIA DECLARADA != DEPENDÊNCIA LIGADA).
   Conserto: `persistencia.dependencias_do_runtime()`, como faz a CLI (`provas/social-micro-prep/sala_social.py`).
   Depois disso, `raw_asset` = 1 nas duas corridas e o ISPRA entra na Sala.
2. **O vídeo da ARPA Valle d'Aosta não entra em T2, e isso está CERTO.** A Admissão diz `NAO` com prova a favor:
   «nao fala de T2, e fala claramente de outro universo (T5: ricerca, istituto; T9: campagna)». Medido no bruto: o
   post da ARPA VdA (20/09) é a **partilha** do post do ISPRA «Ispra a RemTech Expo» (19/09) — a mesma descrição.
   Não é defeito de código; é a régua a fazer o trabalho dela.

Recibos inteiros do orquestrador: `provas/social-micro-prep/recibo-db-*.json`.

**E um defeito real apareceu no caminho** (é o conserto abaixo): o item social entrava na Sala com
`tempo_lugar_evidencia` **na de omissão** («pousado antes da migration 033»), e as precisões — `SECOND` da data,
`COUNTRY` do lugar — morriam antes da porta.

## CONSERTO+TESTE

- **Onde:** `orquestrador/orquestrador.py`. Quando não há STRUCTURED (o vídeo social vai pela rota do bruto), o
  `correr` mandava `INGRESSO.PARA_A_PORTA` à porta tal e qual. Só a rota documental
  (`item_documental_para_a_porta`) chamava `_fato_do_texto`, que monta `TEMPO_LUGAR_EVIDENCIA`.
- **O conserto:** `item_do_bruto_para_a_porta(item)` — lê de volta, pelo mesmo mapa (`ing.PARA_A_PORTA`), a data
  de publicação com a base e as precisões, chama o **mesmo** `_fato_do_texto` (D63: «ieri» só a partir da
  publicação provada) e devolve uma cópia com `tempo_lugar_evidencia`. O que o coletor provou vence o texto; um
  item que já traz evidência passa intacto; ausência sai `NAO SEI`, nunca inventada.
- **Teste:** `tests/test_social_bruto_leva_a_evidencia.py` — 8 testes, com o **item real da porta** da corrida
  descartável (`tests/dados/item-social-ispra-porta.json`). **Mutação:** `provas/_mutantes_social_bruto.py`
  **5/5 mortos** (bruto sem leitura · precisões ficam para trás · publicação vira data do facto · mexe no item da
  entrada · inventa precisão).
- **Nada partido:** as 22 suítes que importam o orquestrador (561 testes) dão **as mesmas 8 falhas antes e depois**
  do conserto (lista comparada linha a linha; são falhas de base desta máquina — mapa da porta, YouTube C2,
  colisão de nome curto `mutacao.py`, `test_correr_julga_a_unidade_da_fronteira`).

## PROVA_SALA_DESCARTAVEL

Banco descartável próprio (`provas/a_porta_cli_liga_o_banco.Bancada`, 32 migrações), cópia `C:/ens-sm` =
`ce28040c` + o conserto, envelopes sociais remontados a partir do bruto REAL de 24/09 com o código de produção
(`provas/social-micro-prep/replay_social.py`), orquestrador `so_a_porta` + `colheita_da_corrida` (zero rede).
Banco desligado no fim de cada corrida; LOCK-PESADO tomado e libertado.

| corrida | fonte | universo | Sala | `published_at` + base + precisão | `source_location` + base + precisão |
|---|---|---|---|---|---|
| IT-T5-2026-09-26-015614-bff70f97e3d49b3c | IT-T5-193 ISPRA | T5 | **1 linha** | 2026-09-19T09:38:04.511Z · «PLATAFORMA — LinkedIn, pagina publica do post, JSON_LD_VideoObject.datePublished» · **SECOND** | ITALY · «PAIS da ficha do site oficial isprambiente.gov.it no Atlas (IT-T2-009)…» · **COUNTRY** |
| IT-T2-2026-09-26-015750-08fdce0639fee4bd | IT-T2-170 ARPA VdA | T2 | 0 (NAO com prova: é T5) | — | — |
| IT-T5-2026-09-26-020012-9ca33fe8527143c5 | IT-T2-170 ARPA VdA | **T5 — DIAGNÓSTICO** | 1 linha | 2026-09-20T08:51:07.434Z · mesma base · **SECOND** | ITALY · «…arpa.vda.it no Atlas (IT-T2-022)…» · **COUNTRY** |

`completude_tempo_lugar` nas duas linhas: `PUBLICACAO: PROVADA`, `LOCAL_DA_FONTE: PROVADA`, `DATA_DO_FATO: NAO SEI`,
`LOCAL_DO_FATO: NAO SEI`. A data do facto fica NÃO SEI **com o porquê**: o post diz «Oggi» sem marca de que é o
próprio dia (D64), e a data de publicação nunca preenche esse campo.

⚠️ **A 3.ª linha é DIAGNÓSTICO, não veredito.** Perguntei T5 só para mostrar que a data e o lugar da ARPA atravessam
quando a pergunta cabe. Quem escolhe o universo é o pedido (humano), não esta prova.

Saídas: `provas/social-micro-prep/sala-sm3.out`, `sala-diag.out`.

## PROVA_TETO

- **Sobre as corridas descartáveis:** `py provas/prova_teto_dominio.py --livro C:/ens-sm/data/collection-ledger/italy/runs.ndjson --onda provas/social-micro-prep/onda-descartavel.txt`
  → **`PROVA_TETO_DOMINIO=NAO_SEI` (código 2)**, 3 corridas sem linha no livro, 0 pedidos.
  É a resposta certa: o replay não corre o Scrap nem vai à rede, e por isso não escreve linha; a prova recusa-se
  a contar isso como zero. Saída: `provas/social-micro-prep/prova-teto-descartavel.json`.
- **A contagem em si** (o que vai fechar a prova na micro real): `tests/test_prova_teto_social.py` **22/22 OK** nesta
  árvore, sem rede — servidor local conta os pedidos e o Scrap escreve `CORTESIA.PEDIDOS_POR_HOST` igual ao
  servidor; `yt-dlp` real com `--print-traffic`; youtube.com + googlevideo.com no mesmo orçamento (D41);
  linkedin.com e licdn.com separados; corrida que rebenta escreve `ABORTED` com os pedidos.
- **O que isto NÃO prova:** que uma corrida real do LinkedIn/YouTube fica ≤5 por domínio. Isso só a micro mede.

## PLANO_MICRO (não corrido)

Regras comuns: cópia do robô **com rede fechada** até a missão abrir; fila **filtrada** às contas abaixo
(`curadoria/ensaio_so_linkedin.py --tipo …` rebenta se aparecer tarefa de rede fora do filtro); egresso pelo portão
de consenso (`superficie/rede.py`) antes e depois; **prova-teto logo a seguir a cada onda**, sobre as linhas do
`runs.ndjson`. Se der FAIL ou NAO_SEI → parar e reportar, não repetir.

### LinkedIn — 2 contas por onda, `teto=1` (1 vídeo por conta)

Pedidos por conta, lidos no código (`coleta/adaptador_linkedin.video_da_pagina_publica`): página da empresa
(linkedin.com) 1 · página do post (linkedin.com) 1 · bytes do vídeo (licdn.com) 1 · legenda (licdn.com) 0-1.
**Previstos por onda de 2 contas: linkedin.com 4, licdn.com 2-4.** ⚠️ Margem de 1 no linkedin.com: cada
redireccionamento conta como pedido (`it.linkedin.com` → `www`), e 2 saltos passam o teto. Isto é PREVISÃO do
código, **não medida** — a 1.ª onda é a medida.

| onda | contas (slug · candidata · site oficial que prova) |
|---|---|
| L1 | `ispra_2` · CAND-0118 · isprambiente.gov.it — `arpa-valle-d-aosta` · CAND-0133 · arpa.vda.it |
| L2 | `cia-agricoltori-italiani` · CAND-0112 · cia.it — `consorzio-tutela-grana-padano` · CAND-0103 · granapadano.it |
| L3 | `gruppocaviro` · CAND-0094 · caviro.com — `certisbelchim-italia` · CAND-0114 · certisbelchim.it |
| L4 | `italmopa` · CAND-0119 · italmopa.com — `macfrut-fiera` · CAND-0097 · macfrut.com |
| L5 | `dipartimento-di-scienze-agrarie-ambientali` · CAND-0105 · disaa.unimi.it (sozinha) |

**SOURCE_ID: NÃO SEI ainda.** No vivo as 9 são candidatas `POLICY_BLOCK` sem número (medido: nenhuma aparece em
`curadoria/italy_contracts_curator.json` do vivo). Os números da cópia (IT-T5-193, IT-T2-170…) **não valem** para o
vivo (CAND-nnnn/SOURCE_ID colidem entre cópias). Lêem-se no livro vivo **depois** do QUALIFY (plano de instalação).
Universo de cada pedido: o território que o QUALIFY der. ⚠️ A ARPA VdA partilha posts do ISPRA: em T2 a porta
pode voltar a dizer NAO — é resposta válida, não falha da micro.

### YouTube — 1 canal por onda, 1 vídeo (fase `audio-youtube`)

Canais novos (sem número no vivo; os 50 canais que já são fonte ficam fora da micro): Cifo (CAND-0190),
Olio Officina (CAND-0219), Società Entomologica Italiana (CAND-0221), Regione Lombardia (CAND-0289),
ARPAT (CAND-0469), Regione Campania (CAND-0377), CAND-0300, CAND-0423, CAND-0873, CAND-0877, CAND-0335/0332
(o mesmo canal, duas candidatas). Ordem sugerida: os que têm nome e site oficial primeiro (Cifo, Olio Officina,
SEI, ARPAT).

⚠️ **Pedidos previstos: NÃO SEI, e podem passar de 5.** O `yt-dlp` pede a página, o player e a API interna em
youtube.com e o áudio em googlevideo.com — **o mesmo orçamento (D41)**. Nenhuma corrida real foi contada até hoje
(o canário de 24/09 é anterior à contagem). Previsão a olho: youtube.com 3-4 + googlevideo.com 1-2 = **4-6**.
E os pedidos do `yt-dlp` **não passam pelo portão** do `scrap_http`: são contados depois (`--print-traffic`), não
travados antes. Por isso: **1 canal, 1 vídeo curto (<10 min), e a prova-teto logo a seguir**; se >5, a micro
YouTube pára e o dono decide.
⚠️ **Buraco que continua:** o `VIDEO_ID` vem da fase `canal-youtube` (API oficial), cuja chave só existe no GitHub
Actions. Sem ela, o vídeo tem de ser escolhido por quem corre a micro, e isso fica escrito no pedido.

## PLANO_INSTALACAO (o coordenador instala; eu não)

1. Juntar `social-micro-v1` à linha viva (traz a PROVA-TETO-SOCIAL + o conserto do orquestrador). Só código,
   testes e provas; nenhum livro vivo mudado.
2. Parar o bot (`curadoria/PARAR.flag`) e esperar a volta acabar.
3. `py curadoria/semear_qualify_social.py` (só mostra) → conferir as 9 do LinkedIn; depois
   `py curadoria/semear_qualify_social.py --aplicar --vivo`. Para o YouTube, o mesmo com `--tipo YOUTUBE`.
4. Tirar o `PARAR.flag`; o worker faz QUALIFY → número, contrato (com `SOURCE_LOCATION` do site oficial) e rota.
5. Ler os SOURCE_ID novos no livro vivo e **escrever a fila filtrada da micro** com eles.
6. Micro (missão própria, rede autorizada): ondas L1…L5 e Y1…, prova-teto a cada onda.
7. Depois do canário de cada conta: `py curadoria/regua_social.py --corridas <resultados.json> --aplicar --vivo`
   (bot parado outra vez) para READY_FOR_COLLECTION.
8. Nada disto toca a Sala real até a Admissão; as linhas entram pela porta canónica.

## MAPA

**MAPA = IGUAL.** Cadeia corrida com LOCK-PESADO (23:13-23:18): `REGERAR 0` → commit 8ece54e2 →
`SYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio` → `IMPRESSAO_DO_CARIMBO=IGUAL` → `CADEIA=OK`.
A 1.ª passagem reprovou só em P9 (6 ficheiros de prova sem peça: os 4 desta missão e os 2 mutantes,
incl. o da PROVA-TETO-SOCIAL que já vinha sem peça); declarados em `C-SUPERFICIE-SCRAP-V1` (b6d8ecce).
O que o validador escreveu na árvore foi reposto (`git checkout --` das geradas), como manda a nota.

## PROVAS FORA DO GIT

Tudo o que é prova pequena está no ramo, em `provas/social-micro-prep/`. Fica fora (grande, ou cópia de livros vivos):

| caminho | sha256 |
|---|---|
| `C:/ens-sm/data/colheita/scrap/IT-T2-2026-09-26-013122-d2a62bb995556b9c/ENVELOPE.json` | 37afe12a6924d4ea91b5a635df859b69718a08477d4cdfd1a4fd4c1e49a52c50 |
| `C:/ens-sm/data/colheita/scrap/IT-T5-2026-09-26-013213-c16b45abc2778073/ENVELOPE.json` | ef6eef1e860b42048025faf2d91ba9640dc21e546d19b1d82ed8cf130fd25ae0 |
| `C:/soc2/sala-orq-IT-T5-193.txt` (saída do orquestrador) | 8e5f9831882fcd5f51ac7c3cead96c63ed7593a403f9e7159ac2ad4c6b37bec0 |

## EM PALAVRAS SIMPLES

- **Por que a Sala ficava vazia?** Duas coisas. A primeira era culpa minha: eu ligava a máquina de teste sem ligar
  o banco, como um liquidificador sem copo — girava, mas nada ficava guardado. Consertei o meu teste.
  A segunda não é defeito: o vídeo da ARPA Valle d'Aosta é uma **partilha** de um post do ISPRA, que fala de
  pesquisa. A porta perguntou «isto é ambiente regional (T2)?» e respondeu «não, é pesquisa (T5)», com a prova.
- **Achei um defeito de verdade no caminho.** O vídeo entrava com a data e o lugar, mas sem a «etiqueta de
  precisão» (a data vale até ao segundo; o lugar vale até ao país). Era como mandar a encomenda sem a nota fiscal.
  Consertei, com 8 testes e 5 sabotagens de propósito — as 5 foram apanhadas.
- **Provado numa Sala de mentira:** o vídeo do ISPRA entra com data 19/09 às 09:38 (até ao segundo) e lugar
  Itália (até ao país), cada um com a sua base. A data do facto fica «NÃO SEI», com o porquê.
- **Prova-teto:** nas corridas de mentira ela diz «NÃO SEI», e está certa: não houve pedido nenhum à internet para
  contar. A contagem de verdade só aparece na micro real; os 22 testes mostram que a régua conta certo.
- **Plano:** LinkedIn de 2 em 2 contas (4 pedidos previstos ao linkedin.com, teto 5 — margem apertada, de 1);
  YouTube 1 canal de cada vez, e aqui **não sei** se cabe em 5 — pode passar. Por isso a prova-teto corre logo
  depois de cada onda, e se passar, pára.
- **Nada foi instalado, nada foi coletado, a Sala real não foi tocada.**
