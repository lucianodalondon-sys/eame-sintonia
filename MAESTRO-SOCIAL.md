# MAESTRO-SOCIAL — a rodada social num comando, o baixador que não desperdiça, a marca «mesmo vídeo» e a D80 (26/09)

Ramo **`maestro-social-v2`** = **`freio-social-v2`** (35109baa = vivo `69b0e23f` + só o freio) + os commits desta
missão por cherry-pick, sem conflito. Instalação em fila: `freio-social-v2` → `maestro-social-v2`, **os dois ff-only**
sobre `69b0e23f`. (O `maestro-social-v1` era o mesmo trabalho sobre os commits do freio sem a nota da v2; fica como
história.) Sem rede (servidores locais em 127.0.0.1; `HTTP(S)_PROXY=127.0.0.1:9`), vivo e Sala real não tocados,
nada instalado, **SEM MAPA** (a INTEGRA regera; os ficheiros novos vão declarados).

## 1 · O MAESTRO — `ferramentas/maestro_social/maestro_social.py`

```
py ferramentas/maestro_social/maestro_social.py --so-plano [--canario] [--fontes=A,B] [--saida=<pasta>]
py ferramentas/maestro_social/maestro_social.py --correr --autorizado-pelo-dono --saida=<pasta nova>
        [--canario] [--fontes=A,B] [--videos=IT-T5-192:VIDEOID,...] [--retomar]
py ferramentas/maestro_social/maestro_social.py --relatorio --estado=<pasta>/MAESTRO-SOCIAL-ESTADO.json
```

O molde é o condutor da web (`onda_web.py`), com o que é próprio das redes:

- **Rodadas** de `plano_onda_social.rodadas()`: até 2 contas LinkedIn (`teto=1` no pedido, C2) + 1 vídeo YouTube por
  onda, com o previsto por domínio; um plano que não cabe no teto **não corre**.
- **Freio antes do pedido:** cada onda tem o SEU livro (`<saida>/ONDA-nn/TETO-ONDA.json`) em `SINTONIA_TETO_ONDA`,
  herdado por orquestrador → Scrap → yt-dlp com freio. O pedido que passaria de 5 por domínio não sai.
- **VPN antes e depois de cada fonte**, pelo dono (`superficie/rede.py`, consenso de 3, via
  `micro_coleta.medir_egresso`). Fora de IT → PARA.
- **Prova-teto no fim de cada onda** (`prova_teto_dominio.verificar`). FAIL ou NAO_SEI → PARA.
- **Estado + `--retomar`:** `MAESTRO-SOCIAL-ESTADO.json` gravado a cada fonte; `--retomar` continua na primeira fonte
  por decidir, com o MESMO plano e o MESMO livro da onda a meio (a onda não recomeça do zero). Sem `--retomar`, uma
  pasta com estado recusa (rodada nova = pasta nova).
- **`--relatorio --estado=`** escreve `MAESTRO-SOCIAL-RELATORIO.md`; o estado traz `FONTES[]` no formato que
  `micro_coleta relatorio --estado=` já lê (SOURCE_ID, RUN_ID, CORREU, STATUS, GATE, EGRESSO).
- **`--canario`:** as contas sociais só ficam READY depois do canário, e o canário social É uma colheita do Scrap (o
  Curator pára em CANARY_PENDING por desenho). Com `--canario` entram as SCRAP_FASE em CANARY_PENDING cuja ÚNICA falta
  é o portão; sem ele, só ELIGIBLE. **É o modo da micro social** (as 18 contas do vivo estão CANARY_PENDING — D80).
- **YouTube:** a listagem `canal-youtube` usa a API oficial (chave só no GitHub). Sem chave no ambiente, corre
  `audio-youtube` do vídeo dado em `--videos=SID:ID`; sem nenhum dos dois, a fonte não corre
  (`SEM_VIDEO_E_SEM_CHAVE`) — isso não é FAILED.
- **Disjuntores:** egresso · > 30 min · 3 FAILED seguidas · livro da onda acima do teto · prova-teto ≠ PASS. Ao parar
  escreve uma linha em `auditoria-madrugada/bc4-aviso-vivo.txt` (o mesmo aviso da onda web).

Testes `tests/test_maestro_social.py` (12, sem rede: o freio, a linha do livro de corridas e a prova-teto são os
REAIS; egresso, orquestrador e portão são dublos): M1 a 2.ª conta da onda só tem o que sobrou (servidor: 5 pedidos,
o 6.º não sai; recusa registada; prova-teto PASS; o pedido leva `teto=1`) · cada onda livro novo · VPN antes e depois
· prova-teto que não passa pára · **retomar** continua sem relançar e no mesmo livro · YouTube sem vídeo/chave e
com vídeo · o estado lê-se pelo relatório do runbook · `--canario` · plano que não cabe.

⚠️ **Um erro meu, corrigido:** a 1.ª versão destes testes escreveu **8 avisos falsos de PAROU** no
`bc4-aviso-vivo.txt` real (05:41). Removi só essas 8 linhas, com cópia antes (`C:/soc2/bc4-aviso-vivo.antes-da-limpeza.txt`)
e uma NOTA no próprio ficheiro a dizer o que tirei; os testes passaram a escrever num ficheiro temporário, e um
teste confere que o aviso sai lá. Nas corridas seguintes (testes e mutação) o sha256 do aviso real ficou igual.

## 2 · O BAIXADOR — `ferramentas/youtube_transcrever.argumentos_do_yt_dlp`

Um só sítio para os argumentos (o transcritor e as provas usam os mesmos). Acrescenta:
`--http-chunk-size 50M` · `--retries 1 --fragment-retries 1 --extractor-retries 1` ·
`--match-filter "duration <= N"` (N = `SINTONIA_YT_DURACAO_MAX_S`, omissão 540 s) · `--print after_filter:… --no-simulate`
(o marcador que distingue «filtrado» de «falhou»).

**Medido no YouTube de mentira (yt-dlp REAL, o intermediário local não repassa nada):**
| caso | antes | agora |
|---|---|---|
| áudio 25 MiB, 5 min | 6 pedidos (3 + 3 fatias) — o freio recusaria o 6.º | **4** (3 + 1 fatia) |
| vídeo de 15 min | descarregava | **3** (só a extracção), nada ao googlevideo, `VIDEO_LONGO_DEMAIS` |

Testes `tests/test_baixador_social.py` (5).

## 3 · A MARCA «MESMO VÍDEO» NA SALA — só PROPOSTA 037 (medido: não dá sem migração)

- **O caderno de revisões não serve:** a 033 fecha-o numa lista (`revisao_so_de_campo_revisivel`: tempo, lugar,
  completude, chaves) e a identidade não se revê. Os json que existem (`fato`, `tempo_lugar_evidencia`,
  `janela_declarada`, `completude_tempo_lugar`) dizem outra coisa — pôr o vídeo lá era misturar.
- **A proposta** (`supabase/propostas/037_a_sala_diz_qual_video_e_o_mesmo.sql` + `037_desfazer.sql`), **fora de
  `supabase/migrations`** para nenhuma Sala (descartável ou real) a aplicar sozinha: uma **tabela ao lado**
  (`sala_de_espera_video`, como a gaveta da 033) — **nenhuma coluna nova na Sala**, a impressão das corridas não
  muda; uma linha por item com identidade CONHECIDA (a regra recusa `NAO SEI`: **UNKNOWN não funde**);
  `mesmo_video_que` null (o primeiro) ou {SOURCE_ID, RUN_ID, …}; só acrescenta (trigger); vista
  `sala_de_espera_videos` (um vídeo, uma linha, quantos itens).
- **O escritor** `admissao/video_na_sala.py` — **não ligado** (ligá-lo depois do `pousar` é do dono da Sala).
  Testes `tests/test_video_na_sala.py` (6): UNKNOWN sem linha; a partilha leva de quem é; a regra da lei, do
  escritor e da proposta é a mesma; a proposta não toca em `sala_de_espera` nem está nas migrações.
- **Ensaio descartável** (`provas/migracao_037_ensaio_descartavel.py`, com a LOCK-PESADO): ver §7.

## 4 · D80 — os posts de pesquisadores entram como CANDIDATOS com a prova da página oficial (desenho + lei)

**Medido antes de desenhar:** as 24 candidatas-pessoa já têm a IDENTIDADE provada por página oficial (ex.:
`ibba.cnr.it/staff/barbara-menin/`, sha256 guardado — P5/P4b). Mas **nenhuma tem um POST**, e o acervo colhido do
vivo (`data/collection-store`, 48 MB, 50 fontes) tem **0** links para posts do LinkedIn. A primeira fonte realista
de URLs de posts é a **lista do dono**, depois páginas de eventos/projetos.

**A candidata** (uma por post): `TIPO=LINKEDIN_POST_PESSOA`, `URL` (a forma pública
`/posts/<slug>-activity-<id>-<hash>` ou `/feed/update/urn:li:activity:<id>`), `PESSOA` (a CAND-11xx do perfil),
`PESSOA_NOME`, `ORIGEM` ∈ {PAGINA_OFICIAL, LISTA_DO_DONO, BUSCA_PUBLICA} e, para página oficial, `PROVA_PAGINA` =
{URL, CLASSE ∈ UNIVERSIDADE/EMPREGADOR/EVENTO/PROJETO, SHA256 dos bytes que NÓS guardámos, LIDA_EM}.

**A lei** `leis/prova_de_post_de_pessoa.py` (feita, sem rede) — `julgar()`:
- **RECUSADA** se a URL não é post público (perfil `/in/`, login…) — pela MESMA trava do coletor
  (`adaptador_linkedin._alvo_e_post_publico`, D24), sem segunda cópia;
- **SO_CANDIDATA** para a busca pública («descobre, não prova»), para página cujo host não é de casa oficial
  CONHECIDA, ou a quem falte nos bytes o **link do post** (o activity id) ou o **nome** da pessoa (todos os pedaços;
  um apelido só não basta), ou cujos bytes não batam com o sha256;
- **PROVADA** só com página oficial conhecida que CITA e LIGA — ou lista do dono com referência.
- **Na colheita** (segundo cadeado, sem pedido a mais): `autor_confere(CREATOR_URL do post, perfil da pessoa)` —
  a página do post declara o autor; diferente = o vídeo não é desta pessoa e não se atribui; sem autor = NÃO SEI.
Testes `tests/test_prova_de_post_de_pessoa.py` (8) + 2 mutantes.

**A estrada (o que falta, com dono):** (a) lista do dono ou páginas oficiais colhidas pela onda WEB normal (robots,
freio) → (b) `julgar` → PROVADA vira candidata na FILA-UNICA com a prova escrita → (c) QUALIFY de post-de-pessoa e a
fase `video-post-linkedin` no Scrap (C5, que chama `video_de_post_publico`) → (d) o maestro corre-a como uma conta
LinkedIn (1 pedido à página do post + 1-2 ao licdn) → (e) `autor_confere` na colheita. Sem perfil, login, cookie.

## 5 · Testes, mutação, regressão

- Novos nesta missão: maestro 12 · baixador 5 · vídeo na Sala 6 · D80 8 (+ os 48 do freio/dedup/C2 sobre a base nova).
- **Mutação `provas/_mutantes_maestro_social.py`: 13/13 mortos** (livro da onda; um livro para todas; VPN antes;
  VPN depois; prova-teto; retomar; `--canario`; fatia; filtro de duração; nome do vídeo longo; UNKNOWN na Sala; D80
  busca pública; D80 um pedaço do nome). E a do freio (`_mutantes_freio_social.py`) continua no ramo.
- **Regressão** (41 suítes de Scrap/YouTube/LinkedIn/teto/onda/social, base `69b0e23f` vs ramo): **as mesmas 14
  falhas herdadas** antes e depois; 844 → 891 testes.

## 6 · Pedidos aos donos

1. **Dono da Sala:** decidir a 037 (tabela ao lado; §3) e ligar `video_na_sala.registar` depois do `pousar`, com a
   ordem de cada item. Até lá a marca vive no envelope do Scrap e no `VIDEOS-SOCIAIS.ndjson`.
2. **Scrap + Curator (C5):** a fase `video-post-linkedin` e o QUALIFY de post-de-pessoa, sobre `julgar`/`autor_confere`.
3. **Dono (D80):** a lista de posts, se for essa a primeira via (formato em §4).

## 7 · Ensaio da 037 (Sala descartável)

Corrido com a LOCK-PESADO (07:25-07:27; a 1.ª tentativa às 07:03 rebentou ANTES da 037 por codificação: o `psql`
recebia o SQL pela linha de comando do Windows e o `·` do comentário chegou como 0xb7 — passou a ir pela entrada em
UTF-8, no ensaio e no escritor). Resultado inteiro em `provas/maestro-social/ENSAIO-037.json`:

- Sala descartável da cópia `C:/ens-sm` (32 migrações), com os **2 itens reais** do canário LinkedIn de 24/09 pousados
  pelo orquestrador (ISPRA IT-T5-193; ARPA VdA IT-T2-170 com universo T5 — diagnóstico) → **037 aplicada**.
- As unidades carimbadas pela lei: as duas com `LINKEDIN:urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ`; a da ARPA com
  `MESMO_VIDEO_QUE` → ISPRA. Escritor: `REGISTADO` ×2.
- `sala_de_espera_video`: ISPRA `null` (o primeiro), ARPA → {ISPRA}. **Vista: 1 vídeo, 2 itens, 1 primeiro.**
- **Recusados pelo banco:** `NAO SEI` (`video_identity_conhecida`) · UPDATE e DELETE (`SALA_VIDEO_SO_ACRESCENTA`) ·
  linha sem item na Sala (chave estrangeira).
- `sala_de_espera` com as mesmas 2 linhas antes, depois, e depois de **desfazer** (tabela e vista saíram). Banco
  desligado.

## EM PALAVRAS SIMPLES

- **O maestro.** Agora um comando só roda a rodada social inteira: confere a VPN antes e depois de cada conta, usa o
  "caderno de vagas" da rodada (o freio: o pedido que passaria de 5 por site não sai), confere no fim que ninguém
  passou do limite, e para se algo der errado. Se parar no meio, dá para **continuar de onde parou** sem refazer
  nada e sem ganhar vagas novas de presente.
- **O baixador.** Um vídeo de 25 MB gastava 6 pedidos (passava do limite); agora gasta 4. Um vídeo longo demais
  (mais de 9 min) nem começa a baixar — gasta só 3 e diz "longo demais".
- **"É o mesmo vídeo" na Sala.** Não dá sem mexer na estrutura da Sala. Fiz a proposta 037: uma tabelinha ao lado
  (não mexe na Sala), que só aceita vídeo com RG e nunca apaga. Fica guardada fora do caminho automático até o dono
  da Sala dizer sim.
- **Posts dos pesquisadores (D80).** Escrevi a regra: um post só vale se uma página oficial (universidade, evento,
  projeto) mostrar o nome da pessoa **e** o link do post, ou se vier da sua lista. Achado: no acervo que já temos,
  **nenhuma** página liga um post do LinkedIn — então o primeiro caminho realista é a sua lista.
- **Um erro meu:** os meus testes escreveram 8 avisos falsos de "parou" no ficheiro de avisos do coordenador. Tirei só
  essas 8 linhas (guardei cópia) e deixei nota; os testes agora escrevem noutro lugar.
- **Nada foi instalado, coletado ou mexido no vivo.**
