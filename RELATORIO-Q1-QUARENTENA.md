# Q1 — QUARENTENA DO «NÃO SEI» DO DETECTOR (D11, opção C)

Branch `quarentena-naosei-v1` (de `origin/unificacao-v1` @ 5a16d077). Serviços vivos
intocados; Collection não correu; nada na Sala. Ensaio: `curadoria/ENSAIO-QUARENTENA-NAOSEI-V1.json`.

## Estado usado: o que JÁ existia

A Bíblia já nomeia o estado lógico (COL-LAW-044: `RAW · DERIVED · ADMITTED · READY ·
QUARANTINED`) e manda usar a estrutura existente (COL-LAW-027). No código, o dono do
destino de cada documento é a porta (`C-ADMISSAO`, `admissao/admissao.py`, livro
`data/samples/LIVRO-DE-DECISOES.json`), e o seu `NAO_SEI` («não há prova suficiente
para dizer sim ou não») é exactamente o NÃO SEI do detector. **Classe antes do
rótulo: nenhum estado novo, nenhum registo novo.** A quarentena é `NAO_SEI` com
`regra = materia` e `evidencia.estado = QUARENTENA`, com o retrato do detector e o
sha256 da página; o bruto fica intacto; o replay (`--so-a-porta`) volta a julgá-la.

## O achado que obrigou a ligar um caminho

O detector só corria ao nível da FONTE (canário, prova da listagem). **Nenhuma
página colhida passava por ele.** Ligação mínima, sem mexer no detector (LD3):
o derivador de HTML (tem os bytes; é chamado também no REUSED/replay) entrega o
retrato → `derivacao_forward` → estruturação → item → pergunta `materia` da porta,
com a política da LD3 (`politica_nao_sei`, ACTIVA = QUARENTENA). Sem retrato (PDF,
vídeo) a pergunta não se aplica. `VERSAO_DA_REGRA` 5 → 6.

## Ensaio offline (detector actual, sha256 das páginas conferido)

| | original | controlo LD2 |
|---|---|---|
| páginas rotuladas | 109 capas + 37 matérias | 49 capas + 20 matérias (8 vazias e 1 ambígua fora) |
| em quarentena | **34** (26 capas + 8 matérias) | **19** (18 capas + 1 matéria) |
| capas que entram | **37/109** (sem quarentena: 63) | **10/49** (sem quarentena: 28) |
| notícias retidas em quarentena | **8/37** | **1/20** |
| ⚠️ notícias barradas como capa | **6/37** | **4/20** |

A última linha não foi decidida pela D11: a política da LD3 barra sempre o que o
detector chama capa, e ele erra. Barradas = `NAO` no livro, reprocessáveis — mas
barradas. **Decisão para o dono.**

## Saídas e vigilância

Só duas saídas: o detector mudado e provado dá outro veredito no replay, ou uma
decisão humana registada em `data/samples/QUARENTENA-DECISOES-HUMANAS.jsonl` (por
sha256 da página). Ao sair, a página passa pelas perguntas seguintes da porta.
`painel_da_quarentena()`: tamanho, idade, saídas; **ALARME** se a mais antiga tem mais
de 14 dias e nada saiu em 14 dias, ou se passa de 300 páginas → volta ao dono.

## Testes

`tests/test_quarentena_naosei.py` 22 + `test_politica_nao_sei` (actualizado para a
D11). Mutação 14/14 (quarentena→passa e quarentena→descarta reprovam). Regressão,
em worktrees limpas, comparada por nome: base 1701 testes / 196 vermelhos; nova
1725 / 196 — 1 vermelho novo (`test_M5`, carimbo do mapa) curado pela cadeia.
