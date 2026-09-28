# L3 · Onde os 2 fatos da R9 moram no Casco original

Correcao do dono (28/09 ~20:37), item 2: «identificar o destino SEMANTICAMENTE CORRETO para FATO CLIMATICO com
DATA + LUGAR + EVIDENCIA [...] Se nao existir destino correto: DESTINO_DE_PRODUTO_AINDA_NAO_DEFINIDO — nao
invente, nao mude o significado de nenhuma ferramenta.»

```
DESTINO_CORRETO_DOS_2_FATOS_NO_CASCO = DESTINO_DE_PRODUTO_AINDA_NAO_DEFINIDO
```

Nenhum codigo foi escrito para os por em tela nenhuma. Nada foi revertido porque nada tinha sido escrito
(a missao foi parada antes da primeira edicao; `git log` do ramo comeca em `9f20eeb23`).

## Os 2 objetos (lidos do pote, SHA256SUMS conferido 10/10)

Pote `PARA-O-CASCO-R9/POTE-R9-PARA_CLIENTE.json` · sha256 do ficheiro `9aa916e3…d963` · canonico `276b490f…7feb`
· corrida `IR-56c79b0c78fc3fa1e747`.

| objeto | especie (dita pela Intelligence) | fato | FACT_TIME | lugar do fato | cultura / problema |
|---|---|---|---|---|---|
| `AF-2cc19f200815fa06` | SINAL | scarto termico +2..+6 °C | 2026-09-07/2026-09-13 | «su gran parte della Puglia» | NAO SEI / NAO SEI |
| `AF-11c9e6b6ee8caa6e` | SINAL | piogge 46.8 mm e 32,8 mm | 2026-09-07/2026-09-13 | «in provincia di Lecce a Nociglia e Otranto» | NAO SEI / NAO SEI |

Os dois vem do mesmo boletim (ARIF, Notiziario Agrometeorologico N38, publicado 2026-09-16, colhido 2026-09-20).
`LIGACAO_ADAMA.ESTADO = NAO_SEI`, com `FALTA = CULTURA · PROBLEMA · SUBSTANCIA`: nenhum produto ADAMA ligado.

## As telas do casco original, uma por uma

| tela (rota) | ficheiro:linha | o que ela significa | cabe um fato climatico sem cultura? |
|---|---|---|---|
| Radar das Oportunidades (`meeting`/`radar`) | `italia-portale/client/portale.html:491` | oportunidades comerciais do motor | **NAO** — decisao do dono: nao sao oportunidades |
| Finestre Colturali (`windows`) | `portale.html:1617`; frase `italy-i18n.js:101` («quando la coltura ha bisogno di protezione e quando deve iniziare il lavoro commerciale») | janela por CULTURA × problema | **NAO** — os 2 tem CULTURA = NAO SEI; um fato de clima nao e uma janela (AGENTS.md: «data regulatoria nao vira janela agronomica», o mesmo vale para o clima) |
| Rete Commerciale di Campo (`field`) | `portale.html:1882`; `italy-i18n.js:91` | mensagens dos vendedores (WhatsApp), com selo DEMO | **NAO** — outro canal, outra origem |
| Archivio segnali (`future`) | `portale.html:2950`; le so `futureSignals` em `portale.html:10367` | sinal sobre o FUTURO, com «prossima finestra» e «portafoglio» no cartao | **NAO** — os 2 sao fatos passados (07–13/09) sem janela nem produto |
| Archivio (`archive`) | `portale.html:3537`; `italy-i18n.js:250` | indice de DOCUMENTOS (ciencia, mercado, concorrencia, vozes, eventos, noticias, janelas) | **NAO** como fato — o boletim-documento ja tem lugar la (BULLETIN), a afirmacao de dentro dele nao |

## O que EXISTE e nao e tela

O modelo do casco ja tem a familia certa para isto — e ela esta vazia de proposito:

- `italia-portale/client/italy-app-model.js:4290-4305` — `agrometConditions`, «agrometeorological observations,
  each with the scope its own source declares»; o comentario diz «No upstream table yet. An empty collection is a
  valid answer».
- rotulo: `italy-app-model.js:4787` «Condizioni agrometeo».
- **nenhuma tela a desenha.** So aparece para dar NOME a uma evidencia (`portale.html:6571`) e o clique dela manda
  para `future` (`portale.html:6609`), que nao le esta familia (`portale.html:10367` le so `futureSignals`).
- e o mapa de familia a marca como `REGULATORY_FUTURE_FACT` (`portale.html:6585`) — o que nao e: um fato de clima
  nao e um fato regulatorio. Nao corrigido aqui (nao e desta missao); dito.

## Dois avisos para quem decide

1. **O proprio pote poe os 2 no compartimento `windows`** (`VISTAS_DO_CASCO = ['windows']`). O leitor de debug do
   casco segue isso (`sintonia-pote-casco.js:165-173`) e desenha-os na rota `#windows`, dentro da faixa
   «EXPERIMENTAL · NOT FOR THE CLIENT» (`portale.html:3645`). Pela tabela de cima, esse compartimento tambem nao e o
   sentido certo para um fato de clima sem cultura. Quem escolhe o compartimento e a Intelligence
   (`pacote/pote_intelligence_casco.py`); o casco nao o muda (INT-LAW-023). Pergunta para a Intelligence.
2. Para haver destino e preciso uma decisao de PRODUTO: ou uma vista original para «Condizioni agrometeo» (a
   familia ja existe no modelo), ou outra. Isso e do dono; esta missao nao a inventa.
