# RELATÓRIO — YT2 · O YOUTUBE CHEGA À SALA (UNIVERSO NO COMANDO + RÉGUA T8 COM GABARITO)

Branch `youtube-regua-t8-v1`, a partir de `youtube-oficial-v1` @ `7f651aa7`, 2026-09-23.
Rotas de YouTube tal como o Scrap as declara (D17.4); código do Scrap intocado; nada
pago; nenhuma conta; nada na Sala real (Postgres descartável novo por lote).

## ENTREGA

```
UNIVERSO_NO_COMANDO   YES — recusa UNIVERSO_NAO_DECLARADO ANTES da rede (o executor nao
                      e chamado); com universo, o executor corre. tests/test_universo_antes_da_rede.py
                      8/0 · 4 mutantes, 4 mortos. Achado ao lado: FILTRO_NAO_CONSUMIDO
                      rebentava no manifesto — agora diz porque e sai com 1.
GABARITO_T8           SIM 20 (12 canais) · NAO 28 (16 canais) · NAO_SEI 9
                      77 videos tentados (29 canais, <=3 por canal) · 57 transcritos ·
                      20 sem transcricao (16 o YouTube nao entregou, 4 sem fala)
                      egresso IT 77/77 (Palermo) · ASR na GPU · protocolo e as 3 rondas de
                      selecao commitados ANTES de cada download
REGUA_T8              precisao 0,769 (10/13) · recall 0,50 (10/20) — medido DENTRO da amostra
                      controlo negativo: 3 de 28 NAO entraram como SIM
                      4 ramos provados (valido SIM · insuficiente NAO_SEI · incompativel NAO ·
                      invalido barrado no «legivel»)
VIZINHOS_INTOCADOS    YES — IT_VERDICTS_CHANGED = 0 em 798 julgamentos (133 textos: lote-76 +
                      gabarito × T3 T4 T5 T7 T9 T10), contra a admissao da revisao anterior
CANARIO_T8            Sala de teste +1 com AQUISICAO NOVA: zaEk8LE6SOQ (IT-T8-001) · RAW sha256
                      0167e225… · DERIVED 3.026 B · Admission T8 SIM · Sala 0 -> 1 (WAITING)
                      (+1 antes, pela porta de reprocesso, X35K1b5_B78, quando o YouTube pediu
                      «prove que nao e robo»)
TESTS                 test_regua_t8 17/0 · test_universo_antes_da_rede 8/0 · testes da Admission:
                      0 falhas novas contra a base, por nome (as 17 da base continuam as mesmas)
MUTATION              10/10 mortos com execucao provada (4 no universo, 6 na regua — o MA1 so
                      morria na prova da lista; nasceu a prova de comportamento test_11b)
FINAL_HEAD = REMOTE_HEAD   na mensagem de entrega
SYSTEM_MAP_CHECK      na mensagem de entrega
```

## O que fica para outros donos

- `PUBLISHED_AT` e `DOCUMENT_ID` continuam ausentes na rota de áudio — engenheiro do Scrap
  (`scrap-portas-v1`).
- A régua T8 é de modelo (rótulos Claude, `VALIDADO_POR_HUMANO = NAO`). O dono pode validar
  o gabarito como validou o GABARITO-MICRO-V1.
- Para medir T8 fora da amostra é preciso listar vídeos de canais T8 (só 1 dos 28 canais
  amostrados pelo curador é T8): isso pede a fase `canal-youtube` com a chave da Data API,
  que vive no GitHub.

## Erros meus, corrigidos

1. Num lote, o Postgres descartável morreu a meio (outro processo apaga `pg-prova-cli-*`
   do %TEMP%); 5 vídeos foram descarregados e falharam depois. Refeitos; o banco passou a
   ter pasta própria e o arnês confere-o antes de cada vídeo.
2. O primeiro teste do universo esperava que a falha do executor propagasse; o orquestrador
   converte-a em FAILED. Corrigido o teste, não o código.

Detalhe: §197 do `SINTONIA-EAME-KNOW-HOW.md` e `scripts/regua_t8/`.
