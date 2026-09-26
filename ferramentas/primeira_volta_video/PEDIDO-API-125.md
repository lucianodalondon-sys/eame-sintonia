# PEDIDO-API-125 — os metadados dos 125 vídeos dos 9 canais de pesquisa, pela API oficial

Ramo `primeira-volta-video-v1`, **junto ao vivo `278cd489`** (lote 2), ff-only = SIM. **Sem rede.**

## Em palavras simples

- **Para quê:** os 125 vídeos dos 9 canais de pesquisa (UNIBO DISTAL, ISPRA, UNIBA DiSSPA, UNICT Di3A,
  Univ. Bolzano, Fondazione Minoprio, Fondazione Navarra, Cantina Riunite, Confagricoltura Lombardia)
  só existem na Sala como **registos de falha** (o YouTube respondeu «pare», 429, a 20/09). Sem título
  nem duração, não se escolhe o que transcrever.
- **O pedido:** a API oficial devolve título, descrição, data, duração e canal de até 50 vídeos num
  só pedido. Pela fase `video-youtube` do Scrap, a correr no GitHub (onde está a chave).
- ⚠️ **Corrijo o que eu disse:** não são 3 pedidos, são **9** — **um por canal**. O recibo do Scrap
  leva **um** número de fonte; misturar canais no mesmo pedido pregaria vídeos na fonte errada.
  Continua barato: **9 unidades de quota** (de 10 000 por dia), **0** pedidos a `youtube.com`.
- ⚠️ **Achei um defeito, e consertei-o neste ramo:** pelo workflow, a lista chega como **texto**
  («a,b,c») e o Scrap pedia à API **letras soltas** («1», «S», «p»…): medido a seco, 2 pedidos por
  canal, ~60 «IDs» de uma letra, **0 vídeos**, quota gasta. Com o conserto: **1 pedido por canal,
  15 de 15 IDs certos, 125 itens**.

## O que falta para correr (por ordem)

| # | O quê | Estado | Quem |
|---|---|---|---|
| 1 | **A chave** `YOUTUBE_DATA_API_KEY` | ✅ existe no segredo do GitHub; o passo 6 do `sintonia-scrap.yml` já a entrega à fase `video-youtube` (nunca impressa). Nesta máquina: ausente (conferido sem ler o valor). Nada a fazer. | — |
| 2 | **O conserto dos IDs em texto** (`coleta/adaptador_youtube.youtube_metadata`) | ✅ feito neste ramo (a0abcef0), com teste; **por instalar** | coordenador |
| 3 | **P2 no workflow** — hoje `assunto_do_alvo_da_fonte` só conhece `IT-T8-*`/`IT-T9-*`: os 9 são **T5 e T7** → `FONTE_SEM_APELIDO`. E a Admissão **exige** `--filtro universo=Tn` (recusa sem ele), que o ramo do YouTube do workflow **não** passa. | ❌ por fazer (texto exacto abaixo) | coordenador (workflow) |
| 4 | **D20: quem apaga ou renova aos 30 dias.** Os 125 itens vêm da rota `youtube-data-api-v3:videos.list`, levam o prazo de 30 dias escrito (medido a seco), e **entram na Sala** (a fase é COLHEITA; o job usa `SUPABASE_DB_URL`). Mas `social_envelope.vencido()` **não é chamada por ninguém**: não há trabalho que apague ou renove. A D20.3 diz que, até isso estar provado, esta rota não pode prometer retenção. | ❌ decisão | **dono** |
| 5 | **Os runners** `SINTONIA-EAME-LOCAL`/`-2` | NÃO SEI se estão ligados (último diagnóstico 11/09 e 13/09) | coordenador |
| 6 | **Disparar o workflow**: `gh` com sessão ou a interface web (o próprio workflow `curator-youtube-handles.yml` anota que o `gh` desta máquina não tem sessão) | — | coordenador |

Não é preciso: o `--pelo-scrap` dos 9 (eles continuam `YOUTUBE_CHANNEL_FEED` · `RETRY_AFTER` no vivo,
e o orquestrador não trava por isso), nem o P1 (as marcas `OWNER_AUTHORIZED`/`PLATFORM_POLICY_STATUS`
só importam ao canário da régua social, não a estes metadados). O Atlas conhece os 9 (9 de 9).

### O texto do P2 (para o `sintonia-scrap.yml`, não aplicado)

```bash
          assunto_do_alvo_da_fonte() {
            case "$1" in
              IT-T5-*) echo 'colete ciencia' ;;        # leis/territorios.APELIDOS: ciencia -> T5
              IT-T7-*) echo 'colete cooperativas' ;;   # cooperativas -> T7
              IT-T8-*) echo 'colete agricultores' ;;
              IT-T9-*) echo 'colete concorrentes' ;;
              *) return 1 ;;
            esac
          }
          universo_da_fonte() { echo "$1" | sed -E 's/^IT-(T[0-9]+)-.*/\1/'; }
```
e, nos ramos `canal-youtube` e `video-youtube`, acrescentar `--filtro universo="$(universo_da_fonte "$FONTE_YT")"`.
A Admissão só tem régua para T3, T4, T5, T7 e T9 (`admissao.PERGUNTAS_DO_UNIVERSO`): T5 e T7 servem.

## As 9 corridas (`PEDIDO-API-125.json`)

| Fonte | Canal | Vídeos | Chamadas `videos.list` | Universo · frase |
|---|---|---|---|---|
| IT-T5-042 | Fondazione F.lli Navarra | 15 | 1 | T5 · colete ciencia |
| IT-T5-043 | UNIBO DISTAL | 15 | 1 | T5 · colete ciencia |
| IT-T5-044 | Fondazione Minoprio | 15 | 1 | T5 · colete ciencia |
| IT-T5-045 | ISPRA | 15 | 1 | T5 · colete ciencia |
| IT-T5-047 | UNIBA DiSSPA | 15 | 1 | T5 · colete ciencia |
| IT-T5-048 | UNICT Di3A | 15 | 1 | T5 · colete ciencia |
| IT-T5-050 | Libera Università di Bolzano | 15 | 1 | T5 · colete ciencia |
| IT-T7-016 | Cantina Riunite & CIV | 15 | 1 | T7 · colete cooperativas |
| IT-T7-018 | Confagricoltura Lombardia | 5 | 1 | T7 · colete cooperativas |
| **Total** | | **125** | **9** (9 unidades) | 0 `youtube.com` |

Cada linha do JSON traz o comando do workflow (`gh workflow run sintonia-scrap.yml --ref <ramo do vivo>
-f fase=video-youtube -f fonte=<SID> -f videos=<15 ids> -f runner=1`) e o do orquestrador equivalente.
Uma corrida de cada vez; 9 pedidos a `www.googleapis.com` no total (1 por corrida, teto D38 folgado).

## O ensaio a seco (`PEDIDO-API-125-SECO.json`, `pedido_api_125.py --seco`)

Código verdadeiro do Scrap (`scrap_colheita.colher('video-youtube', …)`), numa cópia deste ramo; chave
falsa só no processo; transporte da API trocado por respostas literais; proxy fechado. A lista passa
como o workflow a entrega (texto).

| | Pedidos por canal | IDs pedidos | IDs de 11 caracteres | Itens | Prazo D20 no item |
|---|---|---|---|---|---|
| **sem o conserto** | 2 | ~60 | **0** | **0** | — |
| **com o conserto** | **1** | 15 (5) | **15 (5)** | **15 (5)** | `YOUTUBE_DATA_API_30D`, 30 dias |

**Regressão:** os 11 ficheiros de teste do YouTube, com e sem o conserto: **as mesmas 8 falhas** nos dois
(`test_c2_youtube_oficial` 4, `test_c3_youtube_cutover` 3, `test_youtube_oficial` 1 — todas já no vivo
`278cd489`), **0 novas**. Duas delas são o desencontro já anotado no CANAIS-41 (P5): a matriz escolhe a
página pública do canal para `youtube.channel.discovery`, e o executor corre a API.

## O que isto não prova

- Que a API devolve os 125 (vídeos apagados ou privados voltam em `MISSING`, e isso é informação).
- Que os runners estão ligados, e em que banco o job grava (a Sala real, pelo segredo; não conferido daqui).
