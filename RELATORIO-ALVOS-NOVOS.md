# RELATÓRIO — ALVOS-NOVOS (D40)

Ramo `capa-materia-v1` (contém a produção `servico-20260923-0923 @ 7cdb7ea4`). **Não instalado.**

## 1 · Onde está o D40 (dono único da escolha)

| o quê | ficheiro:linha |
|---|---|
| teto de 3 por fonte | `regras/motor_de_rota.mjs:333` — `ALVOS_POR_FONTE_D40 = 3` |
| a escolha | `regras/motor_de_rota.mjs:335` — `escolherAlvosD40(urls, classificar, nomeDe)` |
| a porta | `regras/motor_de_rota.mjs:355` — `alvosDoContrato(..., { classificar })`; ramo `MATCH: "URL"` em `:410`, ramo HTML em `:424` |
| quem pergunta ao livro | `coleta/italy_pilot_collect.mjs:807` — `classificar` usa `decidirSobreDetalhe` (a mesma lei da DEFESA 1) com a memória do livro de observações, construída uma vez antes da corrida |
| vazio honesto | `coleta/italy_pilot_collect.mjs:812` — detalhe `SEM_ALVOS_NOVOS`, `LIVRO: NAO_ESCRITO — nada foi pedido`; os conhecidos somam em `SKIPPED_KNOWN` |

Regra: o índice é lido; cada endereço é classificado **antes do corte** (`CONHECIDO` sai,
`NOVO` fica na ordem do índice, `REVISITA` — TTL vencido de fonte `MUTABLE` — vai para o fim);
corta-se em 3, seja qual for o `MAX_TARGETS` do contrato. Nada foi pedido para decidir: a escolha
gasta zero rede. Sem `classificar` (canários, provas) o motor corta como antes.

## 2 · O teto D38 não foi duplicado

O D38 (5 pedidos por domínio registável por corrida, robots e índice incluídos) vive no transporte
`umaIda()` do ramo `onda2-g3-v1 @ a55c667f`. A escolha **não conta pedidos**: entrega no máximo 3
alvos, e o contador de domínio do transporte é o único ponto de corte. Alvo cortado pelo teto fica
`DEFERRED_BY_COURTESY / TETO_DOMINIO`, como a G3 define.

Junção ensaiada (`git merge-tree`, sem escrever): `coleta/` e `regras/` juntam-se **sem conflito**;
na árvore junta, `node --check` passa e `motor_de_rota_test` dá 57/57. Os 13 conflitos são todos
ficheiros gerados do mapa (`*.generated.json`, `state.generated.json`) e
`docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md` — resolvem-se regerando pela cadeia.

**Combinação com a G3:** o orçamento da cia.it (5 fontes, 1 domínio) acaba na 1.ª fonte da fila
(robots 1 + índice 1 + 3 matérias = 5). As outras 4 ficam adiadas **em todas as corridas** enquanto
a ordem for fixa. A decisão de rodar a ordem (ou não) é do coordenador; não mexi.

## 3 · Testes e mutação

- `regras/motor_de_rota_test.mjs`: 57/57 (7 novos D40: conhecido sai antes do corte e só o índice é
  pedido; máx. 3 com `MAX_TARGETS` 1 e 30; ordem estável; NOVO antes de REVISITA; tudo conhecido →
  vazio com a conta, sem erro nem alvo inventado; MATCH HTML; sem `classificar` = comportamento
  antigo).
- `incrementalidade_test` 31/31, `recollection_test` 31/31, `paridade_test` 32/32.
- `italy_contract_test`: 348 passam, 77 falham — **as mesmas 19 linhas FAIL** antes e depois
  (comparadas ordenadas); são de base, não do D40.
- Mutação na cópia `C:/capa-base @ 32dde8fc`: **9/9 mortos** (`scripts/capa_materia/MUTACAO-D40-V1.json`).

## 4 · Medição (25/09, 07:33 UTC)

Rede: portão de egresso por consenso **PASS IT** (2 votos IT, 1 US discordante). **14 pedidos, 1 por
domínio**, só o índice, nenhum robô coletor (D41.3), nenhuma matéria. `robots.txt` não foi re-pedido
para caber em 1 pedido por domínio: estas páginas passaram pelo robots do coletor na 1.ª onda (24/09).
Índices fora do Git em `C:/Users/London1/alvos-novos-20260925/indices/`, sha256 de cada um em
`scripts/capa_materia/INDICES-D40-V1.json`. Livro da produção lido só para leitura:
`observations.ndjson` sha256 `a054c336…e3e0e5`, 169 endereços conhecidos.

| fonte | no índice | já conhecidos | novos | revisitas | docs novos na corrida D40+D38 | jeito antigo + D38 |
|---|---|---|---|---|---|---|
| IT-T10-018 myfruit | 32 | 21 | 11 | 0 | 3 | 0 |
| IT-T10-021 plantgest | 4 | 1 | 3 | 0 | 3 | 0 |
| IT-T10-022 zootecnica | 9 | 9 | 0 | 0 | 0 (vazio honesto) | 0 |
| IT-T2-034 arpa marche | 10 | 1 | 9 | 0 | 3 | 0 |
| IT-T2-051 arpae | 8 | 1 | 7 | 0 | 3 | 1 |
| IT-T5-090 istat | 42 | 1 | 41 | 0 | 3 | 0 |
| IT-T7-017 riuniteciv | 55 | 31 | 24 | 0 | 3 | 0 |
| IT-T7-021 etvilloresi | 17 | 2 | 15 | 0 | 3 | 1 |
| IT-T7-033 chianticlassico | 15 | 15 | 0 | 0 | 0 (vazio honesto) | 0 |
| IT-T7-042 balsamico | 10 | 0 | 0 | 10 | 0 (3 pedidos em revisita) | 0 |
| IT-T7-043 federchimica | 2 | 2 | 0 | 0 | 0 (vazio honesto) | 0 |
| IT-T7-112 cia (AGIA) | 3 | 0 | 3 | 0 | 3 | 1 |
| IT-T7-117 caf-cia | 7 | 1 | 6 | 0 | 3 | 0 |
| IT-T7-118/121/123/135 cia | NÃO MEDIDO | — | — | — | 0 (D38: domínio esgotado) | 0 |
| IT-T7-141 ciatoscana | 11 | 0 | 11 | 0 | 3 | 1 |
| **total** | | | **130** | | **30 em 10 fontes** | **4** |

## 5 · Previsão honesta

- **Documentos novos por corrida:** 30 com D40+D38, contra 4 do jeito antigo com o mesmo teto,
  no mesmo dia, sobre os mesmos índices.
- **Quantos serão SIM na Admissão: NÃO SEI.** Não baixei nenhuma matéria (a missão deu 1 pedido
  por domínio). Leitura pelos **títulos dos endereços** — interpretação, não medida:
  - provavelmente SIM: myfruit 3, plantgest 3 (notícias agrícolas, como os 3 SIM da 1.ª onda);
  - duvidoso: riuniteciv 3 (prémios de lambrusco), cia AGIA 3, arpae 3 e arpa marche 3
    (ambiente, balnear, concursos);
  - provavelmente NÃO: caf-cia 3 (impostos, modelo 730), etvilloresi 3 (moda, eventos),
    istat 3 (páginas de secção do site), **ciatoscana 3 (páginas de lista `comunicati-stampa-2026/2025/2024`
    — capa no lugar de matéria, o mesmo defeito da CAPA-MATERIA, noutro molde)**.
- MICRO: a 1.ª onda deu 3 SIM em 18 = 16,7%. Se só myfruit + plantgest renderem, são ~6 SIM → 6/18
  = 33%. Se o denominador do D35 for documentos julgados, ~6/30 = 20%. Os dois passam de 16,7%,
  **mas dependem da leitura pelos títulos acima**; a prova é a própria corrida.
- A contagem é de hoje: o índice muda; os 130 novos de hoje não são uma taxa por dia.

## 6 · Writeset

```
regras/motor_de_rota.mjs            (D40: ALVOS_POR_FONTE_D40, escolherAlvosD40, opção classificar)
coleta/italy_pilot_collect.mjs      (alvosDe(classificar), classificar pelo livro, SEM_ALVOS_NOVOS)
regras/motor_de_rota_test.mjs       (7 testes D40)
scripts/capa_materia/mutar_d40.py · MUTACAO-D40-V1.json
scripts/capa_materia/buscar_indices_d40.py · INDICES-D40-V1.json
scripts/capa_materia/medir_d40.mjs · MEDICAO-D40-V1.json
RELATORIO-ALVOS-NOVOS.md
system-map/data/architecture.declared.json (C-CAPA-MATERIA) + gerados do mapa
```

Só os dois primeiros mudam o comportamento da coleta. Instalar junto com (ou depois de) a G3, para
o teto D38 estar activo; sem a G3, vale o teto antigo de 5 por host.
