# SOCIAL-ATÉ-A-SALA — as ações A, B, C e D do estudo do coordenador (27/09)

Ramo `claude/social-at-sala-7wu107`, a partir da produção `18461b92d`. Máquina da nuvem (Linux, Python 3.11.15,
Node 22.22.2, PyYAML presente). **Sem rede social nenhuma**: a única rede usada foi o GitHub. Nos testes e no
ensaio a rede ficou fechada (proxy numa porta morta).

**Livros vivos intocados.** `git diff 18461b9 HEAD` não traz `curadoria/*-V1.json` de estado,
`data/collection-ledger` nem `candidatas/FONTES-CANDIDATAS.json`. O mutador confere o sha256 de 6 livros antes e
depois: **0 mudaram**. A ação **E** (teto por conta) é do dono e não foi tocada.

## O que foi feito

### A · Desfazer o POLICY_BLOCK (pelas portas) — decisões D22/D23/D24/D106

| peça | onde |
|---|---|
| **porta da fila** `desbloquear_por_decisao`: POLICY_BLOCK → CANDIDATA. O desbloqueio fica **ao lado** do bloqueio (`DESBLOQUEIO{DECISOES, OWNER_AUTHORIZED=SIM, PLATFORM_POLICY_STATUS, PLATFORM_POLICY_PROVA, QUEM, QUANDO}` + `HISTORICO_DE_ESTADO`) e nada se apaga. Cada tipo só sai pelas decisões que o cobrem: Instagram D22/D106; LinkedIn D23/D24/D106. Falha fechado sem autorização, sem a política medida ou com uma decisão que não cobre o tipo | `candidatas/fonte_nova.py:219`, `:225` |
| **o caminho do Curator** `curadoria/desbloquear_social.py`: fila → livro do ciclo de vida (o CANDIDATA_ID passa de POLICY_BLOCK a DISCOVERED, append-only) → `QUALIFY` na fila de tarefas. O resto é o worker de sempre: QUALIFY → SOURCE_ID → BUILD_CONTRACT (rota do Scrap) → VALIDATE_ROUTE → CANARY_PENDING | `:79` aplicar · `:121` ensaio · `:50` decisões · `:59` política |

A política da plataforma é a que já foi **medida**, nunca uma sonda nova: os termos que a ponte guardou
(URL, data, sha256) e, no LinkedIn, o robots `DISALLOW_ALL` de 2026-09-08 (D37). A D106 é citada pela missão;
**o texto dela não está no repositório** (NÃO SEI o limite exato).

**Ensaio numa CÓPIA dos livros do repositório** (`curadoria/social-sala/ENSAIO-A-NA-COPIA.json`):

```
entram                  94 = 68 LinkedIn + 26 Instagram  (no repo: 69 em POLICY_BLOCK + 25 em CANDIDATA; no vivo o coordenador mediu 94 em POLICY_BLOCK)
QUALIFY                 37 OK · 57 BLOCK   ->  BUILD_CONTRACT 37 OK · VALIDATE_ROUTE 37 OK · tarefas com rede 0
GANHAM SOURCE_ID        37 LinkedIn de ORGANIZAÇÃO, as 37 em CANARY_PENDING (contrato video-linkedin)
PARAM (57), e porquê    26 Instagram  — sem rota que liste a conta (a D22 só abre o Reel por URL; profile.discovery = ROUTE_NOT_ALLOWED)
                        24 LinkedIn   — PESSOA (/in/): a rota do Scrap só lê /company/; o vídeo de pessoa (D24) não tem fase
                         4 LinkedIn   — /showcase/: não é alvo do adaptador
                         3 LinkedIn   — território NAO SEI (Valagro, Fieravicola, Interpoma): falta decisão semântica
```

As **mesmas 37 candidatas** ganharam número no ensaio LI-ONDA de 24/09, e os mesmos bloqueios apareceram
(`curadoria/SOC-ONDA2-ENSAIO-QUALIFY-V1.json`: 37 = 37). **Os números não se repetem:** só 4 dos 37 são iguais.
O SOURCE_ID sai do registo de alocação de quem corre, e o do vivo não é o do repositório. **Quem ganha
repete-se; o número, não.**

⚠️ Depois do QUALIFY, as 50 que param por POLICY voltam a `POLICY_BLOCK` **no livro**: 26 Instagram e 24 pessoas
(o worker mapeia BLOCK/POLICY assim). Mas agora o motivo escrito é o **medido** («sem rota que liste a conta» /
«pessoa sem fase»), e já não o TOS da D15. Na fila elas ficam `CANDIDATA`, com o desbloqueio escrito.

### B · A régua social por PROVAS — `curadoria/regua_social.py`

- `provas_sociais` (`:219`): cada item prova **quatro coisas** — a conta de origem, a data de publicação
  (com a precisão declarada), `OWNER_AUTHORIZED=SIM` e a ligação **conta → publicação → mídia**. Ou seja: a conta
  é a do contrato, a página nomeia o id, há sha256 e bytes maiores que zero, e a mídia guardada nomeia a
  publicação. Falta uma → **FALHA, dizendo qual**.
- A função **não recebe a fase**: vale para `audio-youtube`, `captura-reel` e `video-linkedin`. Lê os campos onde
  cada adaptador os escreve (YouTube no topo; Reel em `REEL.*` / `RAW.*`; LinkedIn em `RAW.CREATOR_URL` /
  `RAW.VIDEO_*`).
- A conta do contrato vem de `CHANNEL_ID`, `LINKEDIN_SLUG` ou `INSTAGRAM_HANDLE`. A tabela de pares de fase
  (`FASES_EQUIVALENTES`) saiu.
- Onde entra: `:344`. Os campos de topo mantêm a semântica antiga; os caminhos alternativos só se leem quando o
  topo não tem o campo (`:323`).

**Os 3 casos reais do YT-METADADOS** (`tests/dados/social-sala/YT-METADADOS-3CANAIS.json`). Cada valor diz de que
ficheiro veio.

| caso | antes | agora |
|---|---|---|
| IT-T9-029 | FALHA pelo nome da fase | **READY** (as quatro provas + a D53) |
| IT-T5-165 | FALHA pelo nome da fase | FALHA **só** «sem a mídia adquirida: sha256 + bytes» — o repo guarda os bytes (173 728 504) mas **não o sha256** deste áudio |
| IT-T3-025 | FALHA pelo nome da fase | FALHA, igual à de cima (124 301 512 bytes, sha256 NÃO SEI) |

Com um sha **sintético** (declarado como tal no teste), T5 e T3 ficam READY: a mídia é a única prova que falta.

⚠️ **Ajuste declarado de testes.** Os testes 12, 13 e 15 de `tests/test_d36_envelope_equivalente.py` mediam a lei
antiga («só o par de nomes passa»). A lei nova é a desta missão (decisão delegada da D36: provas, nunca o nome).
A proteção continua medida: o envelope de comentários e a lista do canal **continuam a reprovar**, agora pela
prova que lhes falta.

O mutador `provas/_mutantes_d36_equivalencia.py` foi reapontado ao texto novo. São as **mesmas 9 perguntas**.

### C · YouTube sem chave pelo feed do canal — `coleta/adaptador_youtube.py`

⚠️ **A casa já tinha medido que o feed é proibido.** `Disallow: /feeds/videos.xml` está no robots.txt de
www.youtube.com (medido em 08/09, 20/09 e 24/09). A matriz escreve a linha `feeds/videos.xml` como
**PERMITIDA=NAO / ROUTE_NOT_ALLOWED** (`leis/social_matriz.py:419`), e o próprio cabeçalho dela avisa para
«ninguém voltar a descobrir daqui a três meses» o que já custou medição. **Não contornei.**

O que ficou construído:
- `youtube_canal_sem_chave` (`:1016`) corre **dentro** da fase `canal-youtube` quando não há chave (`:172`).
  Não é um segundo coletor.
- **1 pedido por canal, até 15 vídeos**, cada um com `NATIVE_ID`, `PUBLISHED_AT` (precisão SECOND, base
  «feed Atom `<published>`») e o canal. Entradas de outro canal ou sem id ficam de fora e são contadas.
- Passa pelo **transporte canónico** `scrap_http.buscar_bytes`: robots vivo, teto por domínio do
  `teto_da_onda` e o portão. DTD/ENTITY é recusado.
- **Nasce fechada.** Lê a linha da matriz antes de sair (`:966`). Fechada, recusa com **ZERO pedidos**
  (`:1030`), e a sonda responde exatamente o que respondia (`CREDENTIAL_MISSING`).
- **Abrir é decisão do DONO, escrita na matriz**: uma linha com `PERMITIDA=SIM` + `OWNER_AUTHORIZED=SIM` +
  `PLATFORM_POLICY_STATUS=DISALLOWED`, como a D23 fez no LinkedIn. Aberta, a decisão viaja **nomeada**
  (`autorizacao_do_dono`). Sem ela escrita, o item sai `OWNER_AUTHORIZED=NAO SEI` e a régua não o deixa ficar READY.
- **A alternativa sem chave que JÁ é permitida** existe mas **não traz data**: a página
  `/channel/<id>/videos` (`youtube_canal_publico`). Ela não está ligada a nenhuma fase, e não a liguei: seria
  COLHEITA sem data.

⚠️ **Ajuste declarado de teste.** `tests/test_as_duas_portas_do_scrap.py` deriva do registo a lista das fases que
leem a chave. A sonda de `canal-youtube` passou a ser `pronto_para_canal` (`:1082`), que continua a ler a chave
primeiro. Ela declara isso num atributo (`LE_A_CHAVE`), e o teste passou a aceitá-lo.

### D · Entrada por URL achado — `coleta/social_por_url_achado.py` (novo; peça `C-SOCIAL-POR-URL-ACHADO` no mapa)

- **Entrada**: o formato de `POSTS-PARA-O-SCRAP.jsonl` da `linha_busca` (URL + PROVENIENCIA). A proveniência
  exigida é:
  - `ACHADO_POR_BUSCA`: consulta, motor, posição ≥ 1 e instante ISO;
  - `ACHADO_POR_PESSOA`: quem, onde e instante.

  Sem ela inteira → `REJEITADO` (`:97`).
- ⚠️ `coleta/linha_busca.py` **não está na produção 18461b9**: vive só no ramo `linha-busca-v1` (`0aec389`). Li o
  formato de lá; não trouxe o ficheiro.
- **Endereços** (`:77`): Reel → `captura-reel` (`url`); post de ORGANIZAÇÃO → `video-linkedin` (`pagina` = a
  página dela, teto 2). Um perfil **não é item**.
- **Identidade** (`:136`): o SOURCE_ID vem dos livros do Curator, lidos pelo leitor dele, nunca da URL. Os
  estados possíveis:

  | estado | quando |
  |---|---|
  | `ESPERA_SOURCE_ID` | a conta não tem SOURCE_ID: entra como **candidata pela porta** (`fonte_nova.registar`, só com `--registar --copia` ou `--vivo`+PARAR.flag) |
  | `CONTA_NAO_SEI` | `/reel/<código>` sem conta, ou autor de post que não se sabe se é `/company/` ou `/in/`. Nada se regista adivinhado |
  | `BLOQUEADO_POR_DECISAO` | post de PESSOA: `video_de_post_publico` (D24) existe mas não tem fase, e a D37 tirou-lhe o robots |
  | `IDENTIDADE_EM_COLISAO` | a conta liga a mais de uma fonte |
  | `CONTA_EM_CONFLITO` | a conta que o achado diz não é a do endereço |
  | `DUPLICADO` | o mesmo alvo já está no plano |

- **Proveniência na corrida**: `--anexar` (`:329`) escreve `PROVENIENCIA-DO-ACHADO.json` ao lado do ENVELOPE e
  mede `ALVO_NA_COLHEITA`. A página da organização só serve os posts recentes, e um post achado mais antigo pode
  não vir.
- **Hoje**, com os livros do repo: nenhum Instagram tem SOURCE_ID (os 26 param no QUALIFY), por isso **reel
  achado = candidata + espera**.

## Testes — bateria INTEIRA por nome (`provas/integra_noite/bateria_inteira_por_nome.py`)

| | base `18461b9` | ramo `c3ebff79` |
|---|---|---|
| ficheiros de teste | 393 | 397 (+4 novos) |
| testes corridos | 7 373 | 7 443 |
| falhas por nome | 432 | 433 |

**0 sumidas · 1 nova, e ela foi consertada neste commit.** A falha era
`test_integracao_04a_curator::test_a_pasta_coleta_nao_tem_executor_para_o_feed`: a lei diz que `coleta/` não lê o
livro do Curator pelo nome. O módulo D passou a lê-lo pelo leitor do Curator (`rota_do_scrap_youtube`), e o
teste não foi tocado. Depois do conserto, esse ficheiro volta a ter só a falha que a base já tinha.

Resultados em `provas/social_sala/bateria-{base-18461b9,ramo-c3ebff79}.json`. Os testes novos passam todos:

| ficheiro | testes |
|---|---|
| `test_regua_social_por_provas.py` | 22 |
| `test_youtube_feed_sem_chave.py` | 17 |
| `test_social_por_url_achado.py` | 20 |
| `test_desbloquear_social.py` | 11 |

## Mutação

- `provas/_mutantes_social_ate_a_sala.py`: **37/37 mortas**, 0 livros vivos mudados. B 9, C 9, D 10, A 9.
  - Na primeira corrida sobreviveram 2: «a página não precisa de nomear o id» e «a conta do LinkedIn lê-se de
    qualquer campo».
  - Faltavam casos nos testes; **acrescentei os testes, não mexi no código**.
- `provas/_mutantes_d36_equivalencia.py`: **9/9**.
- `ferramentas/legacy99v4/mutacao.py`: **32/32** (as V1–V8 da D53 continuam a apanhar).

## System Map

Mapa regerado pela cadeia depois de cada `git add`: `SYSTEM_MAP_CHECK=PASS` e
`impressao_da_arvore.py --conferir-carimbo` = **IGUAL**.

Declarado: a peça nova `C-SOCIAL-POR-URL-ACHADO`, o mutador em `C-PROVA-ROTAS-REAIS`, e a frase de `C-SCRAP-SOCIAL`
e `C-PORTA-FONTE` corrigida. **Não recarimbei** (`--stamp`): as peças ficam PENDING até alguém reler.

## A SEQUÊNCIA EXATA para o coordenador, no vivo

```
0  FORA DO VIVO: juntar claude/social-at-sala-7wu107 à produção (18461b92d -> fast-forward); cadeia do mapa; PASS/IGUAL.
1  Medir antes; PARAR o robô (curadoria/PARAR.flag); foto sha256 dos livros (FONTES-CANDIDATAS, LIFECYCLE-LEDGER/-QUEUE/-EVIDENCE,
   SOURCE-ID-ALLOCATION, italy_contracts_curator).
2  py curadoria/desbloquear_social.py                           -> esperado: 94 (68 LinkedIn D23/D24 + 26 Instagram D22)
3  py curadoria/desbloquear_social.py --aplicar --vivo           -> 94 DESBLOQUEADA, 94 QUALIFY na fila   (robô parado)
4  Relançar o robô e deixar ficar IDLE. Esperado, sem rede: 37 LinkedIn -> SOURCE_ID + contrato video-linkedin + CANARY_PENDING;
   57 BLOCK (26 IG sem rota de listar, 24 pessoas, 4 showcase, 3 território). Conferir os 37 CAND contra
   curadoria/social-sala/ENSAIO-A-NA-COPIA.json (os NÚMEROS saem do registo do vivo).
5  COM VPN IT: canário das 37 pelo executor do Scrap:
      py ferramentas/maestro_social/maestro_social.py --so-plano --canario
      py ferramentas/maestro_social/maestro_social.py --correr --autorizado-pelo-dono --canario --saida=<pasta nova>
   (≤ 5 pedidos por domínio/24 h: ~2 contas LinkedIn por dia — é a trava E, do dono.)
6  Régua (robô parado): py curadoria/regua_social.py --corridas <RESULTADOS> --envelopes <ENVELOPES> --aplicar --vivo
   E os 3 canais do YT-METADADOS: a mesma régua sobre os envelopes audio-youtube deles, se existirem no vivo.
   T9-029 deve dar READY; T5-165/T3-025 dependem do AUDIO_SHA256 do envelope real.
7  D (quando houver achados da busca): py coleta/social_por_url_achado.py --plano --achados=<POSTS-PARA-O-SCRAP.jsonl> --saida=PLANO.json
   ; robô parado: ... --registar --vivo (contas sem SOURCE_ID -> candidatas); as linhas PEDIDO correm pelo orquestrador (D28), com VPN IT;
   depois de cada corrida: py coleta/social_por_url_achado.py --anexar --plano=PLANO.json --linha=<n> --run-id=<RUN_ID>
DESFAZER: código -> reset --keep 18461b92d; livros -> a foto do passo 1 (o livro de estados é append-only).
```

**Decisões que ficam para o dono:**

1. **E** — o teto social por conta.
2. **Abrir o feed do YouTube na matriz**: o robots proíbe, e só a decisão escrita o atravessa.
3. **Uma fase para o vídeo de PESSOA por URL de post** (D24): a D37 tirou-lhe a cobertura do robots.
4. **Um contrato de Instagram cuja rota seja o Reel por URL achado**: sem isso, as 26 contas não ganham número.
5. **A ponte (D15)** continua a pôr em POLICY_BLOCK as candidatas LinkedIn/Instagram **novas**.

## EM PALAVRAS SIMPLES

O motor já sabia pegar Reels, vídeos de empresas no LinkedIn e o áudio do YouTube. O que faltava era o caminho
até ele. Abri três pedaços desse caminho e deixei o quarto pronto, à espera da sua decisão.

1. **A proibição antiga foi desfeita com o seu nome escrito ao lado.** No ensaio feito numa cópia, 37 páginas de
   empresas no LinkedIn ganham número de fonte e ficam prontas para o teste. As outras 57 param, cada uma com o
   motivo escrito:
   - 26 contas de Instagram: o Instagram não deixa listar os reels de uma conta;
   - 24 pessoas: o vídeo de pessoa ainda não tem porta no motor;
   - 7 páginas LinkedIn: 4 são subpáginas (showcase) e 3 não têm região.
2. **A porta da Sala deixou de recusar pelo «nome» da etapa.** Agora confere as provas: de que conta veio,
   quando foi publicado, se o senhor autorizou, e se o vídeo guardado é mesmo daquela publicação. Dos 3 vídeos
   reais do YouTube, 1 já passa. Os outros 2 só esbarram numa prova que o repositório não guardou (a impressão
   digital do áudio).
3. **O YouTube sem chave pelo feed do canal ficou construído, mas fechado.** O próprio YouTube proíbe robôs
   nesse endereço, e a casa já tinha medido isso três vezes. Só abre se o senhor escrever a autorização na
   matriz, como fez com o LinkedIn.
4. **Reels e posts achados na busca agora viram pedido para o motor**, com a prova de como foram achados.
   Mas só quando a conta já é uma fonte com número. Se não for, ela entra na fila de candidatas e espera, sem
   número inventado.
