# RELATÓRIO SOC4 — YOUTUBE PRONTO PARA A BIG COLLECTION

> Branch `youtube-pronto-v1` a partir de `origin/unificacao-v1 @ 940f3b14` · 2026-09-23.
> Junta SOC2 + SOC3 (`origin/retencao-youtube-v1 @ f899ed7f`), que ainda não estavam na linha.
> Serviço vivo NÃO tocado · Sala real NÃO tocada · US$ 0 · nenhuma conta · nenhum segredo lido.
> O PC caiu (tela azul, 12:50) a meio da cadeia do mapa; o CHECKPOINT do coordenador (956a3978)
> só tinha 9 ficheiros GERADOS do mapa, nenhum código — a cadeia foi refeita inteira por cima.

```
ROTEAMENTO          = APLICADO em pedido/receitas.py (promover_o_scrap no resolver)
                      50 canais: sem a promoção 6 no Scrap / 34 no executor HTML / 10 sem executor
                                 com a promoção 50 no Scrap; pedido sem fase: inalterado
HANDLES_35          = 13 @handle + 17 /user/ + 1 nome nu → vão à API (31); 3 playlist + 1 /c/ → NÃO vão
                      ferramenta + workflow prontos; resolução sem rede provada pela fronteira do Scrap
DISPARO             = por PUSH (sem gh): run 35895519270 = success → 31 RESOLVIDO / 4 NAO_SUPORTADO
                      (1.º disparo 35894140148 morreu no passo 0: guarda de credencial, 3 achados — corrigidos)
QUALIFY_71          = 50 já são fonte (eram 29) · 10 novas · 7 NAO SEI (território) · 4 sem canal (playlist, /c/)
TESTS               = 5 (roteamento) + 11 (handles) + vizinhos: mesmas falhas da base, por nome
MUTATION            = roteamento 5/5 · handles 8/8
```

## 1. «O YouTube é sempre o Scrap» — aplicado

`pedido/receitas.py`: função nova `promover_o_scrap(execs, fase)` e uma linha no fim de `resolver()`.
Uma fase que o registo `scrap-colheita` declara em `serve_fases` abre o Scrap em QUALQUER
território; pedido sem fase (ou com fase que não é do Scrap) devolve a MESMA lista. Não conflitua
com o `scrap-portas-v1` do engenheiro (ele mexe no `EXECUTORES`, eu no `resolver`) — e a regra usa
a lista dele: as fases de Reel que ele acrescenta passam a abrir o Scrap também.

Medido (`provas/roteamento_youtube_proposta.py`): 50/50 canais no Scrap. Plano do orquestrador
conferido num pedido T2 (`colete clima --filtro fase=canal-youtube …`): `scrap-colheita` primeiro.
Vizinhos (12 módulos de pedido/orquestrador/scrap, 416 testes): as mesmas 3 falhas da base, por nome.

## 2. Os 35 @handle — prontos para o runner

* `curadoria/resolver_handles_youtube.py` pede ao Scrap a capacidade que ELE já tem
  (`youtube.channel.resolve`, `channels.list forHandle/forUsername`, 1 unidade cada) pela fronteira
  canónica `scrap_executor.COLLECT`. Guarda só identidade (handle → channel_id, corrida, hora) em
  `curadoria/RESOLUCAO-HANDLES-YOUTUBE-V1.json` — nada que a regra dos 30 dias tenha de apagar.
* **Armadilha evitada:** o resolvedor do Scrap trata um nome nu como handle; `youtube.com/playlist?list=`
  seria lido como `@playlist` e devolveria o canal de um desconhecido. Playlist e `/c/` nunca vão à API.
* O QUALIFY lê o registo (mesma candidata, mesmo endereço, só RESOLVIDO) — e segue o circuito normal
  (canal já conhecido → reusa o número; D21; NAO SEI sem fabricar).
* Workflow `.github/workflows/curator-youtube-handles.yml`: `workflow_dispatch` OU push de
  `curadoria/PEDIDO-RESOLVER-HANDLES.json`; secret só no passo 2; tectos 0 buscas / 60 unidades;
  commit do registo na mesma branch (é assim que o resultado volta a uma máquina sem `gh`).
* Sem rede, pela fronteira do Scrap com a API falsa: `@handle` → RESOLVIDO, `/user/` vazio →
  NAO_RESOLVIDO, playlist → 0 chamadas; a isca da chave não aparece no registo.

Comando manual (se preferirem a interface): Actions → `curator-youtube-handles` → Run workflow,
branch `youtube-pronto-v1`. Com `gh`: `gh workflow run curator-youtube-handles.yml --ref youtube-pronto-v1`
(precisa de `gh auth login` do dono).

## 3. O disparo e o resultado (GitHub Actions, a chave nunca lida)

1. **1.º disparo** (push de `PEDIDO-RESOLVER-HANDLES.json`, run 35894140148): **falhou no passo 0**,
   a guarda de credencial (`guarda/social_guarda.py`). 3 achados, nenhum segredo real: a isca com forma
   de chave Google num teste da SOC1 (agora declara-se «fake» na própria linha) e 2 caminhos pessoais
   do Windows em documentos da linha (`MISSAO-CANDIDATE-FEEDER-V1.md`, `RELATORIO-CUTOVER.md`,
   trocados por `<HOME>`). Local: 0 achados em 2926 rastreados.
2. **2.º disparo** (run 35895519270): **success**. O bot fez commit do registo (85cfd717):
   **31 RESOLVIDO** (14 `forHandle`, 17 `forUsername`) · **4 NAO_SUPORTADO** (3 playlist, 1 `/c/`).

O que isso muda no QUALIFY (ensaio com a etapa real, lane redirecionada, livros conferidos por md5
antes/depois; `curadoria/SOC4-QUALIFY-YOUTUBE-ENSAIO-V1.json`):

| | antes (SOC3) | agora |
|---|---|---|
| o canal já é uma fonte (reusa o número) | 29 | **50** |
| canal novo, qualifica (território pelo nome ou pela D21) | 5 | **10** |
| NAO SEI — território indeterminado | 2 | **7** |
| NAO SEI — sem channel_id | 35 | **4** (playlist e /c/) |

⚠️ Para olhar com gente (a regra não fabricou, mas a ficha está esquisita):
* **CAND-0183 «Valagro — Youtube ufficiale»** aponta para `@syngenta` e a API devolve o canal da
  Syngenta. Fica NAO SEI (território), e bem — mas o endereço da ficha parece trocado.
* **CAND-0187 «AgroNotizie — canale YouTube»** (`@AgroNotizie`) é OUTRO canal que não o do IT-T8-001
  (`UCUs2Mg7…`): ganha número próprio no ensaio. Dois canais da mesma casa editorial são duas fontes
  (COL-LAW-034), mas vale confirmar.

Os números de fonte do ensaio (IT-T12-128, IT-T5-085, …) são os que o registo daria hoje, não
reservas: o número real é cunhado pelo serviço quando as 11 tarefas QUALIFY forem reabertas
(runbook X2, passo 3).

## Know-how
§202 e §203 (os da SOC2 e SOC3, renumerados porque a 5.ª passagem ocupou §199–§201) e §209 (a unificacao-v1 ja usa §202-§208; a SOC2 la e §205 e a SOC3 e §207).
