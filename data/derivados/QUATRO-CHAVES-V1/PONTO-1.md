# QUATRO-CHAVES-V1 · PONTO 1 — quantos SIM T1/T2 entrariam hoje na Sala

Arvore: producao `servico-20260923-0923` @ `7cdb7ea4` (regra de admissao **v9**: T2 v8 + T1 v9).
Rede FECHADA (proxy 127.0.0.1:9). Sala lida so-leitura (`default_transaction_read_only=on`).
Nada escrito: `admissao.escrever()` nunca chamado.

## Resposta

**0 SIM** nos **111** textos T1/T2 ja guardados (22 fontes T1 + 29 T2; RAW de 18/09 a 24/09).
**A regua NAO e o bloqueio.** O bloqueio e O QUE foi guardado.

| | T1 (20) | T2 (91) |
|---|---|---|
| porta inteira (item montado por `orquestrador.item_documental_para_a_porta`) | NAO 14 · NAO_SEI 4 · sem texto 2 | NAO 76 · NAO_SEI 4 · sem texto 11 |
| capa (pagina de entrada, nao materia) — `admissao/admissao.py:571` `_e_materia` | 4 | **70** |
| quarentena capa/materia | 2 | 3 |
| outro universo (T4/T5/T9/T10) — `admissao/admissao.py:786` `_do_universo` | 8 | 4 |
| T1 sem 2 momentos (`SEM_MOMENTO`) | 2 | — |

As duas T2 da 1.a onda: `IT-T2-034` (ARPA Marche) e `IT-T2-051` (ARPAE) trouxeram **noticias**
(estudo/investigacao; registo), nao boletins -> NAO pelo universo. Na BC5 correram com 0 RAW novo.

**Prova de que a porta ACEITA boletins de verdade** (gabaritos, porta inteira, sem rede):
- T2: 61 boletins ouro=YES -> **41 SIM**; os outros 20 tem `SOURCE_ID = "NAO SEI"` no proprio
  gabarito e caem em `origem` — defeito do ENSAIO, nao da porta. Com origem: **41/41 SIM**.
- T1: 55 ouro=YES -> **51 SIM**, 4 NAO_SEI (igual a regua: `MEDICAO-REGUA-T1-V1` recall 0.927).

**O que bloquearia a MICRO:** o lote apontar outra vez para a pagina de entrada ou para noticias.
Para T1/T2 entrarem, o alvo tem de ser o **boletim** (a pagina/PDF do boletim), nao o INDEX_URL.

**Buraco:** `IT-T2-002` (ARPAV, a serie de referencia da regua T2) tem 16 RAW e 4 derivados na Sala,
mas os **4 textos nao estao no armazem** — nao da para re-julgar. (11 textos T2 e 2 T1 em falta ao todo.)

Ficheiros: `derivados-T1-T2.lista` (111 linhas, lida da Sala), `rejulgar.py.txt`,
`REJULGAMENTO-T1-T2.json`, `rejulgar-RESULTADO.txt`, `porta-nos-gabaritos-RESULTADO.txt`.
A 1.a versao do ensaio (item montado a mao, sem `artifact_type`) dava 98 NAO_SEI por «tempo do fato»:
era defeito do ENSAIO; corrigido usando a funcao da producao.
