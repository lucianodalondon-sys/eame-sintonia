# CENSO DA COLETA — o retrato de hoje

> Medido em 07/09/2026, com `py system-map/scripts/censo_da_coleta.py`.
> Nenhum número aqui veio de memória. Todos podem ser conferidos rodando o
> comando de novo.

---

## A — COMO É HOJE

Não existe **um** caminho da coleta. Existem muitos, e cada um começa sozinho.

```
    (nada coordena)
          |
  92 ficheiros de código, 79 deles com entrada própria
          |
  18 executores saem para fora e trazem coisa
          |
  cada um grava onde acha melhor:
     data/samples/   41 chamadas
     data/raw/       11
     research/        9
          |
    (não há peneira)
          |
  guarda/  ->  a sala de espera
```

---

## B — O QUE ESTÁ ERRADO, com número

| o que se mediu | número | por que importa |
|---|---:|---|
| ficheiros de código na coleta | 92 | |
| **pontos de entrada** | **79** | 79 maneiras de começar uma coleta não é «uma coleta»: são 79 |
| executores que saem para fora | **18** | o número real. Não são 44 — 44 era memória |
| **peças que coordenam mais de um executor** | **0** | não existe orquestrador. O máximo que uma peça coordena são 2, e são todas do Instagram |
| ficheiros que decidem relevância | **1** | só `coleta/youtube_relevancia.py`. Os outros canais não têm peneira |
| **quem escreve o recibo da coleta por código** | **0** | o `RUN-MANIFEST.json` é lido por 5 réguas e preenchido **à mão** |
| coletores que registam o que descartaram | 11 de 44 | medido pelo padrão da coleta: `faltam 33` |
| sem chamador e fora do CI | 49 | **não é lixo automaticamente** — metade são ferramentas de mão |

### As três coisas que mais doem

**1. Não há orquestrador.** Quem quiser coletar precisa saber o nome do script.
Um pedido como *«colete materiais de pesquisadores»* não tem hoje por onde
entrar.

**2. Não há porta de admissão.** O caminho é
`colher → carimbar → guardar tudo`, e não
`colher → carimbar → separar → guardar o que passou`.
A peneira existe para **um** canal de cinco.

**3. O recibo existe e ninguém o preenche.** Este é o achado mais útil do censo,
porque significa que o trabalho é pequeno:

`data/samples/RUN-MANIFEST.json` já tem os campos certos —

```
RUN_ID · ACTOR · ACTOR_VERSION · STARTED_AT · FINISHED_AT · INPUT · QUERY
MISSION · COUNTRY · PLATFORM · COST_USD · ITEM_COUNT_RAW · ITEM_COUNT_NORMALIZED
STATUS · ERROR · EVIDENCE_PATH · RAW_EVIDENCE_PATH · RAW_EVIDENCE_STATE
```

Cinco réguas leem-no (`padrao_da_coleta`, `portao`, `proveniencia`,
`sensor_coleta`, `contrato_ator`). **Nenhum executor o escreve.** Por isso
metade das corridas guardadas diz `NOT_PRESERVED` nos campos de tempo e versão.

Não é preciso inventar um recibo. É preciso fazer os executores assinarem o que
já existe.

---

## C — O QUE SE APROVEITA (e não se toca)

| peça | por que fica |
|---|---|
| `RUN-MANIFEST.json` | o contrato do recibo já está desenhado e já é lido por 5 réguas |
| `regras/proveniencia.py` | carimba de onde veio, no momento em que entra |
| `medidas/fato_local.py` | separa o lugar da fonte do lugar do fato |
| `leis/data_clock.py` | separa o tempo do fato do tempo da captura |
| `medidas/padrao_da_coleta.py` | o chão que só sobe; mede o que falta, não o que está certo |
| `ferramentas/*` | 12 ferramentas; só **um** par com sobreposição real |

**Sobreposição medida:** `instagram_transcrever.py` e `youtube_transcrever.py`
são **31% iguais** linha a linha (107 linhas idênticas, mesmas três funções:
`agora`, `fase_alvos`, `fase_rodar`). É candidato a consolidação — não a
apagar.

`cdp.py` e `navegador.py` **não** partilham função nenhuma: não são duplicados,
apesar do nome sugerir.

---

## D — O QUE FALTA DE VERDADE

Só três responsabilidades estão comprovadamente ausentes:

1. **PEDIDO** — um contrato de entrada que diga *o quê*, sem dizer *como*;
2. **ORQUESTRADOR** — quem responde «qual caminho executar para este pedido»;
3. **PORTA DE ADMISSÃO** — a peneira comum, com `SIM / NÃO / NÃO_SEI /
   NÃO_SE_APLICA`, e o livro que guarda o motivo de cada não.

Tudo o resto já existe e funciona. A missão não é construir um sistema de
coleta: é ligar as peças que já estão lá.
