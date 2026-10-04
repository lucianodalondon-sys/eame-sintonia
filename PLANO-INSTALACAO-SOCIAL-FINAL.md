# PLANO DE INSTALAÇÃO — SOCIAL FINAL (LI-ONDA + YT-ONDA) sobre a produção 7cdb7ea4

Pedido: coordenação 25/09 (D41). **Nada instalado. Instala-se DEPOIS da 2.ª onda web (D35.4).**
Substitui, para a instalação, `PLANO-INSTALACAO-LI-ONDA.md` e `PLANO-INSTALACAO-YT-ONDA.md`. Esses dois ficam
como história dos ensaios anteriores.

## O que se junta (3 pontas)
| ponta | SHA |
|---|---|
| produção `origin/servico-20260923-0923` | **7cdb7ea4** (junção T1 sobre 7b769819) |
| social `origin/social-onda2-v1` | ver o commit citado em «PRONTO PARA INSTALAR» |
| YouTube `origin/yt-metadados-v1` (D36, engenheiro do Scrap) | **8c4dfc1e** |

`git merge` é recusado a esta sessão pela permissão da máquina: **a junção é do coordenador.** Calculei as três
junções duas a duas (`git merge-tree --write-tree`): **0 conflitos de código** em cada par. Conflitam só as geradas
do mapa (`system-map/data/*.generated.json`, `italia-portale/client/system-map/state.generated.json`,
`docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`, `docs/fontes/INDICE-DE-FONTES.md`).
O único ficheiro de código tocado pelas três pontas é `system-map/data/architecture.declared.json`, que junta sozinho.
Já **não é preciso ajuste à mão**: o teste da SOC2 aceita as duas rotas permitidas de listar um canal (commit deste ramo).

## Ensaio (feito, 25/09 ~06:00) — cópia fiel do vivo, REDE FECHADA do princípio ao fim (D41.3)
Cópias `C:/ens-f` (7cdb7ea4 + código juntado) e `C:/ens-f-base` (7cdb7ea4 pura), as duas com os **14 livros do vivo**
(foto: sha em `curadoria/social-final/FOTO-LIVROS-VIVO.sha`). Proxy fechado (`127.0.0.1:9`), só o localhost livre.
```
LIVROS tocados pela juncao           0 de 14
BATERIA producao pura                298 testes · 28 falhas + 2 erros (PyYAML)
BATERIA producao + social + YouTube  425 testes · as MESMAS 28 falhas · 0 novas
MUTACAO                              D37+D41 8/8 · D36 9/9
PORTAO antes                         READY 179 · elegiveis 69
semear LinkedIn -> worker FILTRADO   40 QUALIFY: 37 OK + 3 BLOCK · 37 contratos video-linkedin · 37 CANARY_PENDING
semear YouTube + reabrir 22          QUALIFY 68 OK + 18 BLOCK · 9 numeros novos · 9 contratos canal-youtube · 9 CANARY_PENDING
fila viva pendente (NAO corrida)     14 REPAIR_CONTRACT + 1 CANARY — de outras frentes, fora do filtro
PORTAO depois (sem canario novo)     READY 179 · elegiveis 69 (0 sociais: nenhuma tem canario com o numero de hoje)
PLANO so-plano                       46 fontes sociais com contrato; 0 na onda ate ao canario
DESFAZER                             so os 14 livros sujos; sha256 14/14 iguais
```

### ⚠️ Os números mudaram — as provas de 24/09 já não servem por número
A junção T1 gastou números que estavam livres. **LinkedIn: só 6 de 37 números iguais aos de 24/09. YouTube: 1 de 11.**
A régua social compara o SOURCE_ID do envelope com o do contrato (e o D36 compara o canal), por isso reaproveitar
as provas antigas daria FALHA — nunca um READY errado. **O canário tem de ser refeito na produção, com os números
que o bot cunhar**, lidos do livro vivo e nunca da lista do ensaio.
Dois canais saíram da lista: **CAND-0221** (Società Entomologica Italiana, era um dos 3 canais da prova D36) e
**CAND-0300** ficam `SEMANTIC_REVIEW`. Depois da T1, o site deles já não dá um território único (D21: sem prova, NÃO SEI).

## WRITESET
| passo | escreve | quando | livros do vivo |
|---|---|---|---|
| junção (código) | 95 ficheiros de código/testes/provas/docs (85 da social + 10 do YouTube) + mapa refeito | bot parado | 0 de 14 (ponte: 0 de 3) |
| `semear_qualify_social.py --aplicar --vivo` (LinkedIn) | `LIFECYCLE-QUEUE` +40 | bot parado | 1 |
| `semear_qualify_social.py --tipo YOUTUBE --aplicar --vivo` | `LIFECYCLE-QUEUE` +64 | bot parado | 1 |
| `ensaiar_qualify_youtube.py --reabrir` | `LIFECYCLE-QUEUE` 22 BLOCKED → PENDING | bot parado | 1 |
| worker (relançado) | `SOURCE-ID-ALLOCATION` +46, `italy_contracts_curator.json` +46, `LIFECYCLE-*` | o bot | os de sempre |
| canário (orquestrador, banco descartável, numa CÓPIA com os livros do vivo) | nada no vivo | noites seguintes, com rede autorizada | 0 |
| `regua_social.py --aplicar --vivo` | `LIFECYCLE-LEDGER/-EVIDENCE` | bot parado | 2 |

## Os passos (coordenador)
0. Fora do vivo: `FINAL` = `git merge` de 7cdb7ea4 com `origin/social-onda2-v1` e com `origin/yt-metadados-v1`.
   As geradas levam `--theirs`, e depois a cadeia do mapa (REGERAR → commit → VALIDAR → PORTOES_POS_COMMIT) → PASS. Publicar.
1. Medir: bot @ 7cdb7ea4, ponte @ 84c235da, só os livros sujos, um supervisor, um observador, worker IDLE.
2. Parar + foto dos livros. 3. `git merge --no-ff FINAL` no bot e na ponte. Livros iguais à foto. 4. Relançar.
5. Bot parado: as três linhas de semeadura acima. Relançar; esperar IDLE → 46 CANARY_PENDING.
6. Ler os números do livro vivo: `FAMILY in (LINKEDIN, YOUTUBE)`, estado CANARY_PENDING.
7. **Canário (rede só quando autorizada; fila FILTRADA; teto D38 de 5 pedidos por DOMÍNIO por corrida):**
   - LinkedIn, por conta: 1 pedido a `linkedin.com` + até 2 por vídeo em `dms.licdn.com` (MP4 + legenda).
     Com **teto 1** por conta: 2 contas por corrida (licdn 4, linkedin 2).
     As 9 que já deram vídeo (por slug: gruppocaviro, certisbelchim-italia, arpa-valle-d-aosta, cia-agricoltori-italiani,
     consorzio-tutela-grana-padano, ispra_2, italmopa, macfrut-fiera, dipartimento-di-scienze-agrarie-ambientali)
     cabem em **5 corridas**. As outras 28 depois (ZERO/FALHA em 24/09).
   - YouTube (D38: `youtube.com` + `googlevideo.com` somam no mesmo orçamento): por canal, 1 lista (`canal-youtube`,
     página pública) + 1 áudio (`audio-youtube`: página do vídeo + stream) ≈ 3 pedidos → **1 canal por corrida**;
     9 canais = **9 corridas, 1 lote por noite** (D41.2).
8. Bot parado: `regua_social.py --aplicar --vivo` com os recibos. Portão: 69 → 69 + as que passarem.
9. `plano_onda_social.py` (só plano) → a onda social entra pela porta canónica, com o Pedido montado em processo.

### ↩️ DESFAZER
`git -C $VIVA reset -q --keep 7cdb7ea4` · `git -C $CASA reset -q --keep 84c235da` · livros = foto do passo 2 (provado).
Semeadura e régua são transições append-only: desfazê-las é repor a foto — decisão do coordenador.

## Previsão honesta (medida em 24/09, com os números de então)
LinkedIn: das 9 contas, 12 vídeos com teto 2 (≈ 9 com teto 1), 7 com legenda, 2 itens na Sala.
YouTube: 11/11 som + transcrição e 4/11 na Sala, sem o bloco A; com o bloco A, o engenheiro viu 3/3 READY na cópia dele.
Na produção, cada número tem de passar o seu próprio canário. Até lá, a contagem de sociais prontas é **0**.
