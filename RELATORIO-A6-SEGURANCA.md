# RELATÓRIO A6 · caminhos pessoais e guarda de credencial

**Estado: PARADA por decisão D25 (23/09 ~19:20): a Big Collection vem primeiro.**
O que foi pedido está feito e publicado; o que segue abaixo é a dívida que fica.

## Feito (branch `seguranca-caminhos-v1`, a partir de `origin/unificacao-v1` @ 4ec62114)

- `MISSAO-CANDIDATE-FEEDER-V1.md:223`, `RELATORIO-CUTOVER.md:217` e `:227`: caminho da
  conta Windows substituído pelo marcador `C:\Users\<utilizador>\`.
- `tests/test_prontidao_social_v1.py:29`: a ISCA com forma de chave Google (valor falso)
  passa a montar-se em dois pedaços; valor idêntico.
- `test_a_arvore_versionada_continua_sem_credencial`: FAIL → OK; contraprova (repor o
  caminho → FAIL). `guarda/social_guarda.py`: 2956 ficheiros, 0 achados. Varredura extra
  por formas de chave: 0 credenciais reais.
- SYSTEM_MAP_CHECK = PASS.

## Por fazer

1. **O nome da conta continua em 2198 linhas de 44 ficheiros**, em formas que a guarda
   não vê: 2173 com barra dupla (JSON) e 20 POSIX (`/c/Users/...`). A maior parte são
   medições geradas (`data/samples/RUN-MANIFEST.json` 600, `curadoria/PROPOSTA-CATALOGO-V1.json`
   222, `medidas/lastmile/REDE-*.json` 7 × 137, `medidas/DUAS-PORTAS-REPROCESSAMENTO-V1.json`
   140, `curadoria/GABARITO-T2-T12-V2.json` 129). Não é credencial; é identificação da
   máquina. Decidir antes de mexer: reescrever uma medição gerada muda uma prova guardada.
   O caminho limpo é corrigir os GERADORES (escrever o caminho relativo ou o marcador) e
   regerar, não editar os JSON à mão.
2. **A guarda é cega a essas duas formas.** `guarda/social_guarda.py` só apanha
   `[A-Z]:\Users\...` com barra simples. Alargá-la hoje faria o teste ficar vermelho com
   as 2198 linhas acima; tem de vir junto com o ponto 1, ou com uma lista de dívida
   explícita (`DIVIDA_CONHECIDA`, hoje vazia).
3. Não foi medida a suíte inteira contra a base: só o teste de segurança e a suíte da ISCA
   (`test_prontidao_social_v1`, OK).
