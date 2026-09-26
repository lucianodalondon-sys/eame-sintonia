# ACERVO-PARA-SALA-3 — a página de vídeo é matéria (opção B) + o livro das corridas fora do vivo

Ramo `acervo-para-sala-3-v1`, **rebaseado sobre o vivo `dc0de726`** (fast-forward). **NÃO instalado.** Sem rede;
Sala real e RAW **não tocados** (Sala só lida: `pg_dump` só-leitura às 14:20; a Sala real continuava igual às
17:40: 94 linhas, 88 itens). Ensaios com o `LOCK-PESADO` (15:55–16:14 e 18:31–19:43), Postgres descartável
desligado no fim.

## EM PALAVRAS SIMPLES

**No ensaio, os comandos que você vai rodar põem 17 itens novos na Sala** (94 → 111 linhas). Rodar os mesmos
comandos de novo põe **zero**, ou seja, não duplica nada. Os 17 são:
- os **12** da missão anterior;
- **5 vídeos do YouTube**, os mesmos 5 que a opção B previa:
  - IT-T5-038 e IT-T5-040 (ciência);
  - IT-T7-026, com 2 vídeos (cooperativa);
  - IT-T9-014 (concorrente).

Desses 17:
- **5** têm data de publicação;
- **0** têm data do fato;
- **0** têm lugar do fato;
- **cultura: 0 com o que está instalado hoje; 5 se o D84 for instalado** (4 boletins de clima com oliveira e 1
  vídeo do T9).

Os 5 vídeos entram **sem data de publicação**. Quem lê essa data na página do YouTube é o ramo
`leitor-data-yt-v1`, que ainda não está no vivo.

**O que mudou no código:**
- **Regra V3** no detector de capa: um endereço `youtube.com/watch?v=<código>` é **um** vídeo, nunca uma lista,
  então é matéria.
- **Continuam capa**, como você pediu:
  - canal (`/@nome`, `/channel/`, `/c/`, `/user/`);
  - playlist (`/playlist?list=`);
  - busca, `/shorts/`, `youtu.be/` e a página inicial.
- **Os dois gêmeos juntos:** o Python do Curator e o Node do coletor têm a mesma regra, e um teste confere que
  julgam igual.
- A V3 só abre a porta **"capa ou matéria?"**. Depois dela, o texto do vídeo ainda passa pela régua do assunto
  (universo). Por isso, de 612 vídeos, entram 5:
  - 386 decisões dizem "não se aplica": T8, T11 e T12 não têm régua;
  - a maioria dos outros diz "não achei nada do assunto".

**Dois erros meus, achados pelo ensaio antes de chegarem a você:**
1. O `trazer_livro.py` recusava rodar quando o robô estava **parado**. Era o contrário do certo: o outro comando
   exige o robô parado, então os dois nunca rodariam juntos. Consertado: agora os dois exigem o robô parado.
   A primeira volta do ensaio, feita com o defeito, serviu de medida: **sem trazer o livro, só entram 5**.
2. O teste novo quebrava quando rodava junto com outros testes, por um problema de importação. Consertado.
   O teste irmão `test_c2_juiz` tem o mesmo problema no vivo; é herdado e não mexi nele.

## 1 · A regra V3 (`curadoria/retrato_html.py` + `coleta/retrato_html.mjs`)

```
^https?://(?:www\.|m\.)?youtube\.com/watch\?(?:[^#]*&)?v=[A-Za-z0-9_-]{11}(?:[&#]|$)     (sem maiúsculas)
```

Ordem: **V1** (o INDEX_URL do contrato é capa) → **V3** → **V2** (lista com «leia mais»). Sem retrato não há
veredito. Se o detector já dizia matéria, a regra não se marca como usada.

A porta (`admissao._e_materia`) passa a dizer o motivo: «V3: a página é de UM vídeo (youtube.com/watch?v=) —
matéria, nunca lista; o texto segue para a régua do universo». O gate do coletor (`gate_capa_nao_e_materia`)
deixa passar `watch?v=` e continua a barrar canal e playlist.

Teste `tests/test_v3_pagina_de_video.py` (10):
- 9 endereços de vídeo e 16 que não são (+ vazio e nenhum) (canal, playlist, busca, shorts, youtu.be, raiz, sem `v`, código curto
  ou comprido, `notyoutube.com`, `youtube.com.evil.it`, outro site);
- V1 antes da V3; sem retrato; a página guardada real;
- a porta da Sala (vídeo = SIM pela V3; canal e playlist = NÃO);
- **paridade Node × Python** nos 25 endereços.

## 2 · O ensaio do comando exato (`provas/acervo_para_sala_ensaio_comando.py`)

Uma cópia do código (`2134e092`, este ramo) recebe o **livro do vivo tal como está hoje** (678 + 155 linhas). A
seguir: `PARAR.flag`, cópia da Sala num Postgres descartável e cópia do armazém (2.291 ficheiros com sha256
conferido; 31 que o banco cita não existem em pasta nenhuma, e não afetam estes itens). Depois correm **os
comandos do roteiro, tal como estão escritos**, cada um duas vezes:

| passo | resultado |
|---|---|
| `trazer_livro` (só conta) | +637 observações, +57 corridas, 622 ficheiros; 0 não achados; 0 conflitos |
| `trazer_livro --aplicar` | APLICADO; o livro do vivo fica **intacto no início** (só acrescenta) |
| `trazer_livro --aplicar` outra vez | 0 linhas, 0 ficheiros |
| `reprocessar_lote` (só confere) | 59 corridas · SALA AGORA: 94 |
| `reprocessar_lote --aplicar` | 59/59 exit 0 · **Sala 94 → 111** · 42 min |
| `reprocessar_lote --aplicar` outra vez | 59/59 exit 0 · **Sala 111 → 111** · 18 min |

Sem o passo `trazer_livro` (primeira volta, com o defeito): Sala 94 → **99** (só IT-T10-022 ×4 e IT-T5-049).

Os 17 por universo: T10 6 · T2 5 · T5 3 · T7 2 · T9 1. Decisões dos vídeos (as duas passagens somadas, 1.224):
SIM 10 (= 5 × 2) · NÃO SEI 664 · NÃO SE APLICA 386 · NÃO 164.

## 3 · PARA O COORDENADOR APLICAR (nada foi aplicado)

Pré-condições: este ramo instalado no vivo; `C:/Users/London1/acervo-para-sala/raw.json` na máquina (sha256 em
`scripts/acervo_para_sala/ENTRADAS-2.sha256`); as pastas de `--livros` e `raizes.txt` como hoje.

```bash
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
W=C:/Users/London1/orca/workspaces/eame-sintonia
LIV="$W/*/data/collection-ledger/italy/observations.ndjson;$W/*/data/collection-ledger/italy/runs.ndjson;C:/base6ea/data/collection-ledger/italy/observations.ndjson;C:/base6ea/data/collection-ledger/italy/runs.ndjson;C:/regua-t2-base/data/collection-ledger/italy/observations.ndjson;C:/regua-t2-base/data/collection-ledger/italy/runs.ndjson"
RZ="$(cat C:/Users/London1/reproc-acervo/raizes.txt)"
LISTA=scripts/acervo_para_sala/LOTE-3-CANDIDATAS.json          # a lista ensaiada: sha256 3e714479… com CRLF (checkout no Windows), a119a1e1… no Git (LF); mesmo JSON
cd $V

# 0  instalar o ramo (ff de dc0de726) e fazer o backup da Sala (backup_sala.cmd)
# 1  parar o robo: PARAR.flag na raiz do vivo (os dois comandos recusam sem ele)

# 2  trazer o livro — primeiro SO CONTA; conferir: observations +637, runs +57, BYTES_A_COPIAR 622,
#    BYTES_NAO_ACHADOS [], CONFLITOS []  (numeros diferentes = parar e perguntar)
PYTHONUTF8=1 py -B scripts/acervo_para_sala/trazer_livro.py --arvore $V --lista $LISTA \
  --dados C:/Users/London1/acervo-para-sala --livros "$LIV" --raizes "$RZ"
PYTHONUTF8=1 py -B scripts/acervo_para_sala/trazer_livro.py --arvore $V --lista $LISTA \
  --dados C:/Users/London1/acervo-para-sala --livros "$LIV" --raizes "$RZ" \
  --aplicar --recibo C:/Users/London1/auditoria-madrugada/RECIBO-TRAZER-LIVRO-3.json

# 3  a porta — primeiro SO CONFERE (deve dizer SALA AGORA: 94), depois aplica (~42 min no ensaio)
PYTHONUTF8=1 py -B scripts/acervo_para_sala/reprocessar_lote.py --arvore $V --lista $LISTA
PYTHONUTF8=1 py -B scripts/acervo_para_sala/reprocessar_lote.py --arvore $V --lista $LISTA \
  --aplicar --saida C:/Users/London1/auditoria-madrugada/RECIBO-LOTE-3.json
#    esperado: 59/59 exit 0, SALA 94 -> 111

# 4  tirar o PARAR.flag
```

Se a Sala real mudar antes (outra instalação), o número do passo 3 muda. Os 17 itens não mudam: a Sala é
idempotente por documento.

**O `LIVRO-DE-DECISOES.json` do vivo ganha ~650 decisões** por passagem. É o livro da porta, append-only, como
em qualquer reprocesso.

## 4 · Provas

| | resultado |
|---|---|
| `tests/test_v3_pagina_de_video.py` (novo) | 10/10 (sozinho, com `_gavetas` e na bateria) |
| mutação `medidas-3/mutar_v3.py.txt` | **11/11 mortos por falha de asserção** (V3 desligada py · sem guarda de retrato · qualquer host · sem âncora · id 10–12 · qualquer caminho · regra mesmo se já matéria · V3 antes da V1 · V3 desligada node · node aceita shorts · porta sem motivo V3) |
| regressão: 36 ficheiros (retrato/capa/porta/texto/receitas), vivo `278cd489` × ramo | 688 × 707; **os mesmos 15 vermelhos pelo nome** (herdados) |
| `test_c2_juiz` na bateria com `_gavetas` | 2 erros de import **iguais no vivo `dc0de726`** (herdados) |
| rebase sobre `dc0de726` | limpo; o vivo novo não mexe em nenhum ficheiro deste ramo, fora o `architecture.declared.json` (sem conflito) |

Ficheiros: `ENSAIO-COMANDO-3.json` (o ensaio bom), `ENSAIO-COMANDO-SEM-TRAZER.json` (a primeira volta),
`DECISOES-DO-COMANDO-3.json`, `CULTURA-DOS-17.json`, `LOTE-3-CANDIDATAS.json`, `ENTRADAS-3.sha256`, `medidas-3/`.

## 5 · O que isto NÃO prova

- Que o robô **parado** é suficiente: o ensaio correu sem coletor vivo. Com o robô a escrever no livro durante o
  passo 2, o `trazer_livro` não sabe. Por isso ele e o `reprocessar_lote` recusam sem `PARAR.flag`.
- Os `derived:` dos 17 nasceram na cópia; na Sala real os números serão outros (mesmo conteúdo, mesma receita).
- A cultura (5/17) é medida com o D84 **não instalado**, de uma cópia (`efb78e60`), não pela estrada.
