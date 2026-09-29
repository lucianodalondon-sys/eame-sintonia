# PROTOCOLO DO GABARITO T8 (FARMERS & INFLUENCERS) — escrito ANTES de qualquer rótulo e de qualquer régua

YT2 · 2026-09-23 · método M3c: gabarito primeiro, régua depois, medida no gabarito.
Este ficheiro é commitado ANTES do primeiro download; os rótulos não existem ainda.

## A pergunta de T8

O universo é uma PERGUNTA ao conteúdo, não ao canal (`ALVO != UNIVERSO`). Para T8 a pergunta é:

> **Este conteúdo é a voz ou a prática do campo agrícola?** — um agricultor, técnico de campo,
> agrónomo, criador ou produtor a falar de COMO se produz: práticas de cultivo, defesa, rega,
> fertilização, colheita, maquinaria em uso, variedades em campo, decisões e resultados da
> exploração, e a situação económica da exploração dirigida a quem produz.

Definição de origem: Atlas §T8 (`docs/fontes/ATLAS-DE-FONTES-EAME.md:1129` — agricultores, creators,
canais; eixos REACH · FIELD AUTHORITY · TECHNICAL AUTHORITY · COMMERCIAL INFLUENCE).

## Os rótulos (dois eixos, D2)

`UNIVERSE_MATCH` (é T8?):
- **SIM** — o assunto principal é produção agrícola vista do campo / para quem produz (acima).
- **NAO** — o assunto principal é OUTRO: ambiente/poluição/meteo geral (T2), promoção ou vida
  institucional de universidade/curso (T5 institucional), feira/evento em si, política/legislação
  sem prática, marketing de consumo (spot, receita, prova de vinho), temas não agrícolas.
- **NAO_SEI** — pouca fala, só música, texto ininteligível, ou mistura em que nenhum assunto domina.
  Um NAO_SEI NÃO conta nem como positivo nem como negativo, e fica declarado com o número.

`SINTONIA_RELEVANT` (a ADAMA — defesa de culturas — quereria isto na inteligência?):
- **SIM** — pragas, doenças, infestantes, defesa, prática agronómica, condições de mercado que mudam
  a compra de insumos pelo agricultor; **NAO** — o resto; **NAO_SEI** — não se decide pelo texto.

Os dois eixos são independentes: um T8 pode ser irrelevante (ex.: maquinaria) e um T2 relevante.
O gabarito da régua usa `UNIVERSE_MATCH`; `SINTONIA_RELEVANT` é registado para a Admissão futura.

## Regras do rótulo

1. Lê-se a TRANSCRIÇÃO (texto do ASR), não o título. O título guiou a ESCOLHA do vídeo (abaixo) —
   não o rótulo. Um título «de campo» cuja fala é promocional rotula-se NAO.
2. Rotulador: Claude (Opus 5.5), com o trecho que decidiu citado ao lado. `VALIDADO_POR_HUMANO = NAO`
   até o dono validar — como no GABARITO-MICRO-V1.
3. Nenhuma palavra da régua é escrita antes de o gabarito ter ≥ 20 SIM e ≥ 20 NAO. Se não chegar:
   `NAO PRONTO` com o número, e não se escreve régua.
4. A precisão/recall medida no mesmo gabarito é **medida DENTRO da amostra** — dito assim, sem o
   vender como generalização.

## A coleta do material

Comando canónico do Scrap (D17.4, rota `youtube.public_audio`), 1 vídeo por corrida:

    python orquestrador/orquestrador.py 'colete agricultores' --filtro fase=audio-youtube \
        --filtro fonte=<SOURCE_ID do canal> --filtro video=<VIDEO_ID> --filtro pais=IT --filtro universo=T8

- Canais: os que têm identidade provada (`regras/italy_contracts_onboarded.json`, CHANNEL_ID) e
  IT-T8-001; IDs de vídeo lidos de `curadoria/SOURCE-CHARACTERIZATION-V1.json` (nenhuma listagem nova).
- ≤ 3 vídeos por canal · VPN IT medida antes de CADA vídeo (PARA se não for IT) · US$ 0.
- Base descartável (Postgres novo, Sala de teste nele); checkout isolado (worktree temporária).
- ASR na GPU pelo dono do ASR (`SINTONIA_ASR_DEVICE=AUTO`, carimbado `ASR_DEVICE_USED`).
- Bytes e transcrições FORA do Git; no Git fica o manifesto com sha256 e o trecho que decidiu o rótulo.

A lista escolhida está em `SELECAO-VIDEOS-T8.json`, com o motivo da escolha (pelo título).
