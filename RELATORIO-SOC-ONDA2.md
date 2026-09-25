# RELATÓRIO SOC-ONDA2 — as sociais pelo sistema existente (24/09/2026)

Missão: `auditoria-madrugada/missao-social-onda2.txt` (D16, D22–D24, D28).
Ramo `social-onda2-v1`, feito a partir de `origin/bc4-correcoes-v1` @ cffaad2d. **Nada foi instalado.**
Tudo foi medido numa CÓPIA dos livros vivos: foto das 10:09 da árvore do bot (fca4f2b6),
em `C:/soc2/copia`. Os caminhos e sha256 das provas estão em `curadoria/SOC-ONDA2-PROVAS-FORA-DO-GIT.txt`.

## O que se reutilizou (não reinventado)
- `cac84a45` da CUR-PRONTA (a SOC2): o mesmo commit, aplicado por cherry-pick.
- SOC4, blocos 1 e 2 (`youtube-pronto-v1`): `receitas.promover_o_scrap` no resolver e a resolução dos 31 @handle pela API oficial.
- `0add3b49`: a guarda de credencial limpa.

## Passo 1 — identidade provada (150 candidatas: YouTube 81, LinkedIn 44, Instagram 25)
`curadoria/social_onda2_medir.py` só lê; resultado em `SOC-ONDA2-IDENTIDADE-V1.json`.
Regra usada: o site oficial da própria organização aponta para a conta (D21, condição 2 / D24).

## Passo 2 — QUALIFY e contrato pelo WORKER da casa (`social_onda2_ensaio.py`, cópia)
| | YouTube | LinkedIn | Instagram |
|---|---|---|---|
| número novo (SOURCE_ID) + contrato do Scrap | 11 (`canal-youtube`) | 37 (`video-linkedin`) | 0 |
| já eram fonte (sem número novo) | 51 | 0 | 0 |
| bloqueadas, com o nome do buraco | 19 (11 sem channel_id, 8 sem ligação oficial/território) | 7 (4 `/showcase/`, 3 território NÃO SEI) | 25 POLICY: listar Reels de uma conta = `janela`, ROUTE_NOT_ALLOWED; a D22 abre só o Reel por URL, e há 0 URLs de Reel no acervo |

Mudanças no worker: o LinkedIn sai da lista POLICY (D23). YouTube e LinkedIn só ganham número com a ligação oficial.
O Instagram é bloqueado pela leitura da matriz, e não por uma lista escrita à mão.
Os números são de ENSAIO: no vivo, quem os cunha é o bot, depois da instalação. O re-ensaio deu os mesmos 48 números.

## Passo 3 — canário pela porta canónica (orquestrador → scrap-colheita)
37 contas LinkedIn. Banco descartável próprio, com 31 migrações. Portão de egresso IT antes e depois (37/37 IT).
Teto de 2 itens por conta, 20 s de pausa entre contas, sem login, sem pagamento.
- **1.ª corrida: 3/3 com COLHEITA 0.** O Scrap recusa ancorar um SOURCE_ID que o Atlas não conhece
  (`leis/fonte_do_atlas.conhece`). Conserto: `curadoria/atlas_social.py`, uma ficha YELLOW com a identidade provada,
  no padrão do IT-T8-002.
- **Com a ficha:** 14 contas trouxeram vídeo (21 RAW no banco, 8 legendas, 2 na Sala de Espera). 23 deram ZERO_RESULTS legítimo.

## Passo 4 — quantas chegam a READY (`curadoria/regua_social.py`, lido do recibo)
**9 READY**, 23 continuam CANARY_PENDING (zero legítimo) e 5 ficam CONTRACTED_CANARY_FAILED:
- 2 só tinham republicações de outra organização (ASSAM Marche → «ABC Interreg»; Regione Piemonte → PROALP);
- 1 é empresa ERRADA: o URL da candidata «company/societ» estava cortado e levou a «Societ», no Canadá
  (a régua 1 tinha-a promovido; a régua 2 pára-a);
- 2 com o nome a conferir por humano (CRPV → «Ri.Nova»; UNIBO DISTAL → página em inglês).

Livro da cópia: READY 143 → 152. **Portão (`collection_gate`): elegíveis 37 → 46** (+9 LinkedIn).
Para isso o portão passou a conhecer a régua `SOCIAL/v1` (`ready_split`). Sem ela, as 9 caíam em READY_LEGACY.

YouTube: a fase `canal-youtube` precisa da chave, que só existe no GitHub. A lista de vídeos dos 11 canais
corre no workflow `curator-youtube-soc-onda2`, e o resultado está em `curadoria/CANARIO-YOUTUBE-SOC-ONDA2-VIDEOS.json`
quando o runner o grava. Mesmo com a lista, **nenhum canal YouTube novo chega a READY pela porta local**:
o orquestrador local responde CREDENTIAL_MISSING.

## Passo 5 — plano só-plano (`curadoria/plano_onda_social.py`, `SOC-ONDA2-PLANO-ONDA-SOCIAL-V1.json`)
9 fontes na onda, todas `video-linkedin` → `scrap-colheita`, `correr(so_plano=True)` = PLANO, 0 filtros perdidos.
O Pedido é montado **em processo**: pela CLI, o endereço «agricultural» fez o pedido virar T1 (IT-T5-163).

## Buracos que ficam, cada um com dono
1. **Chave do YouTube só no GitHub**: `sintonia-scrap.yml` não a injecta nas fases canónicas. Dono: coordenador + engenheiro do Scrap.
2. **DOCUMENT_ID_RULE**: o Scrap lê a regra em `regras/italy_contracts.mjs`, e os contratos do Curator não chegam lá.
   O item entra com o NATIVE_ID inteiro e DOCUMENT_ID = NÃO SEI. Dono: CUR-PRONTA/coordenador (ponte livro → tabela).
3. **Número novo → Atlas**: sem ficha, o Scrap colhe 0. `atlas_social.py` é o passo; no vivo, escreve o coordenador.
4. **Teto 2** no contrato é o teto do canário; para a onda, o coordenador decide o teto.
5. **Instagram**: sem rota para listar uma conta. Só uma decisão nova do dono, ou URLs de Reel vindas do acervo, abrem isto.

## Testes
`test_soc_onda2_social` (11), `test_regua_social` (15) e as suítes vizinhas
(soc2, soc4, worker_qualify, d21, ponte_candidatas, contrato_unico, ready_split, collection_gate,
um_so_canario_promove, canario_detalhe, prontidao_social_v1) passam.
O `test_prontidao_social_v1` mudou uma linha: o LinkedIn deixa de ser POLICY no QUALIFY (D23).

## ADENDA (24/09, tarde) — canário YouTube e o portão de consenso
- A junção `bb34d386` foi feita pelo coordenador; mapa regerado por cima (PASS) e publicado.
- `superficie/rede.py` passou a ser o de `origin/egresso-consenso-v1` (commit «traz portao de consenso»).
  A 1.ª tentativa do canário YouTube parou antes de baixar qualquer coisa: o `rede.py` antigo da cópia só
  perguntava ao ipinfo, que estava em 429, e respondia UNKNOWN.
- **Canário YouTube**: 11 canais, 1 vídeo cada. Os VIDEO_ID vieram da fase `canal-youtube`, corrida no GitHub.
  Pela porta canónica local correu a fase `audio-youtube`: **11/11 RAW, 11/11 DERIVED (transcrição), 4 na Sala**,
  egresso IT 11/11. Provas em `curadoria/SOC-ONDA2-CANARIO-YOUTUBE-V1.json`.
- **READY YouTube = 0**, por duas razões medidas:
  1. a fase do contrato é `canal-youtube`, e ela não corre pela porta local (a chave só existe no GitHub);
  2. o item de `audio-youtube` não traz PUBLISHED_AT, OWNER_AUTHORIZED, PLATFORM_POLICY_STATUS nem o canal
     de onde veio. A ligação vídeo↔canal só existe na lista do GitHub. Dono: engenheiro do Scrap
     (o adaptador de áudio carimbar a data e a autorização).
  Não se aplicou FALHA ao livro: a rota funciona, e o que falta é da porta (chave) e do adaptador. As 11 ficam CANARY_PENDING.
- **Defeito meu, corrigido**: a régua comparava a fase da corrida com a fase anotada na própria corrida.
  Agora compara com a fase do CONTRATO (`fase_do_contrato`, com teste). O LinkedIn não muda: 9/23/5.
- Instagram: 0 contas qualificadas, portanto 0 canários — não há rota para listar uma conta (ver passo 2).
