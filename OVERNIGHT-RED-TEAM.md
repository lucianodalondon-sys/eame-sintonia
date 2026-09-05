# RED TEAM DA MADRUGADA

Tentativa deliberada de derrubar o próprio trabalho antes de entregá-lo. Cada teste
é executável; os que passaram estão aqui pelo mesmo motivo dos que falharam.

## O que encontrei — e corrigi

### 1 · Herbicida de cereal listado como resposta para batata *(corrigido)*

`ITF-005` (Cyperus na batata) trazia STOPPER P e DICURAN PLUS em
`PORTFOLIO_MATCHES`, com uma nota dizendo que valem para a **cultura seguinte**
obrigada pela etiqueta do sulfosulfuron. A nota estava certa; **a estrutura estava
errada**. Qualquer consumidor do campo — o frontend, outro script — renderizaria
herbicida de cereal como resposta ADAMA para batata × infestantes.

Corrigido: `PORTFOLIO_MATCHES = []`, `ADAMA_LOCAL_RESPONSE = NO`, e os dois
produtos foram para `PORTFOLIO_MATCHES_ON_FOLLOWING_CROP`, com a cultura seguinte
nomeada e o motivo declarado. **A informação não mudou; o lugar dela mudou.**

## O que testei e passou

| teste | resultado |
|---|---|
| `PRIMARY_MATCH` eleito com vários produtos no par | 0 casos (7 dos 10 sinais e 32 das 43 oportunidades são `null`) |
| produto citado sem par no conjunto publicado | 0, depois da correção acima |
| sinal futuro sem `INVALIDATION_TRIGGER` | 0 — todos os 10 declaram o que os derruba |
| estado promovido a `ACT_NOW` | 0 em 50 ações departamentais |
| cartão sem citação de origem | 0 |
| fonte anterior a 2025 tratada como atual | 0 — a mais antiga é 2025-10-10 |
| região sem `REGION_WHY` | 0 |
| português vazando em campo de cliente | 0 |
| propagação removendo produto de oportunidade | 0 (a união garante) |
| propagação recalculando `SIGNAL`, `WINDOW`, `STATUS` ou `GEOGRAPHY` | 0 |
| alvo genérico `MALATTIE_FUNGINE` publicado como par | 0 |
| grupo (`POMACEE`, `DRUPACEE`, `CUCURBITACEE`) publicado como cultura | 0 |
| `INFESTANTI` publicado para produto não-herbicida | 0 de 548 |
| par publicado sem `PROVENANCE` | 0 de 2313 |
| suíte de testes | 329 passed, 4676 subtests |

## O que continua frágil, dito de frente

1. **A dívida de leitura dos rótulos-matriz.** 142 pares que o conjunto antigo tem
   e o novo não tem carregam `ISSUE_ID` canônico. Concentram-se em sete rótulos de
   centenas de blocos. Enquanto isso não fechar, o conjunto novo **não pode**
   substituir o antigo — só somar-se a ele.

2. **`ITF-004` depende de uma leitura minha da ASR.** A transcrição escreve
   «piroxulam» e «mezzo sulfuron»; li como piroxsulam + metsulfuron pelo contexto
   (a própria fala nomeia as duas famílias químicas). O nome comercial que a ASR
   devolve não é confiável e **não entrou**. O caso está marcado `PARTIAL`.

3. **`ITF-008` e `ITF-010` carregam inferência minha**, e ela está separada num
   campo próprio: `DERIVED_CLAIM_TIME_STATE = HYPOTHESIS`. Nenhuma fonte afirma que
   o Trissolcus causou a queda das capturas, e eu também não afirmo.

4. **1.142 dos 2.313 pares não têm `ISSUE_ID` canônico.** O motor conhece 24
   problemas; o conjunto de rótulos fala 61 alvos. Trinta e sete alvos canônicos
   meus — CICALINE, TRIPIDI, ACARI, COCCINIGLIE, DORIFORA, ELATERIDI e outros — não
   existem no vocabulário do motor. Isso limita quanto do conjunto novo consegue
   chegar às oportunidades, e é lacuna **do motor**, registrada e não contornada.

5. **Não há camada de canal.** Três das ações comerciais estão bloqueadas por
   ausência de dado, não por ausência de sinal.
