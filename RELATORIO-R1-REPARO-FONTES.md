# RELATÓRIO — MISSÃO R1 · REPARAR AS FONTES JÁ ACHADAS

Ramo `reparo-fontes-v1` (de `origin/unificacao-v1` + `origin/bot-impasse-v1`, a B4). Motor: `claude-opus-5-5`.

```
READY na CÓPIA do livro vivo (foto 23/09 18:21Z)   143 -> 179  (+36)
READY no VIVO                                       NÃO INSTALADO — ver §5
NEW_FAILURES_BY_NAME                                NÃO SEI — a medição da suíte nova foi morta por falta de memória
MUTAÇÃO                                             42 mutantes · 37 mortos · 5 equivalentes declarados
SYSTEM_MAP_CHECK                                    PASS (cadeia)
```

## 1 · O que estava errado (medido na foto)

| grupo | quantas | causa medida |
|---|---|---|
| CONTRACTED_CANARY_FAILED | 400 | 344 EMPTY_LIST (molde WordPress: 369 dos 375 contratos), 27 capa, 25 contrato reprovado pelo validador |
| CANARY_PENDING | 102 | nenhuma tarefa aberta; 45 eram EMPTY_LIST re-rotuladas pela reconciliação |
| QUALIFY BLOCKED | 200 | 179 território NÃO SEI pelo nome · 21 YouTube barradas por um texto que o código já não tem |
| SEMANTIC_REVIEW | 198 | as mesmas 179 e outras; 0 com prova nova na casa (DECISOES-SEMANTICAS só dá PAIS≠IT para 7) |

- As 16 receitas da M6Pd **já estavam aplicadas** no vivo (14; IT-T10-018 e IT-T10-022 trocadas pela D10).
- «Aguarda qualificação pelo curator» é o texto do MOTIVO de toda QUALIFY que a ponte cria, não um impasse.

## 2 · O que mudou no código

- `curadoria/reparar_contrato.py` — inferência (≤ 4 pedidos, robots da casa, 2 s por anfitrião, segue redireccionamento) e a porta `aplicar()` (só ACQUISITION; guarda a anterior; validador da casa; PRECISA_DE_REMEDIR).
  Recusas com nome: ENTRADA_INSTITUCIONAL, ENTRADA_E_MATERIA, SEM_FAMILIA_DE_ITENS, FAMILIA_ESTATICA, FAMILIA_E_MENU, ITEM_NAO_E_MATERIA, DUPLICADA.
- `worker.py` — etapa REPAIR_CONTRACT (REPAIRING → CANARY_PENDING + VALIDATE_ROUTE; nunca promove).
- `gatilho_discovery.py` — Nível 0c REPARAR (20 por volta, 1 reparo por fonte; CANARY_PENDING sem tarefa volta a canariar; YouTube do texto antigo desbloqueia; SEMANTIC só volta com prova nova). **Discovery só com reparo pendente = 0** (pedido E).
- `canario.hrefs_da_entrada` — um só dono dos links que o canário vê.
- `scripts/reparo/medir_em_copia.py` e `juntar_bancas.py` — medição em 4 bancas, por fatia de anfitrião.

## 3 · Antes → depois, na cópia (`scripts/reparo/R1-ANTES-DEPOIS-EM-COPIA.json`)

| causa | READY novas | o resto |
|---|---|---|
| A · reparo do contrato | 33 (29 de CANARY_FAILED, 3 de CANARY_PENDING, 1 de RETRY) | 132 item não é matéria · 107 sem família · 76 a entrada é uma notícia · 37 página de serviço · 33 capa no canário · 29 sem identidade · 14 família estática · 10 duplicada · ~10 rede/robots/auth |
| B · re-canário (CANARY_PENDING sem tarefa) | 3 | 3 capa, 1 adiada |
| C · QUALIFY | 0 | 21 YouTube desbloqueadas → 5 ganham SOURCE_ID e ficam CANARY_PENDING (o canário é do Scrap) |
| D · SEMANTIC | 0 | 0 de 179 com prova da casa; ficam SEMANTIC_REVIEW (NÃO SEI) |

Sem o filtro FAMILIA_ESTATICA a mesma cópia deu 143 → 188 (`R1-ANTES-DEPOIS-EM-COPIA-SEM-FILTRO.json`); pelo menos 12 das 42 novas eram páginas fixas (accesso-civico, ufficio-gabinetto, area-personale-tributi).

## 4 · NÃO SEI e ressalvas

- ⚠️ Das 36 READY novas, ~5 continuam duvidosas (páginas fixas com título longo: IT-T12-134, IT-T2-063, IT-T7-105, IT-T7-041, IT-T12-044), e IT-T9-015 aponta para «lavora-con-noi» (contrato antigo, via B). **Ler antes de pôr numa onda da Big Collection (D25).**
- O filtro FAMILIA_ESTATICA é heurística declarada (vocabulário de publicação / número-ano-id / título ≥ 6 palavras). Na amostra tirou 12 fixas e 2 boas (issuu da ARPA Toscana, uma notícia da ARPAL).
- IT-T8-058 correu em todas as bancas (a tarefa já estava na fila da foto); contada uma vez.
- 29 SEM_IDENTIDADE: CANARY_FAILED sem contrato no livro do bot e sem alocação — o contrato vive noutra tabela.
- Mutantes equivalentes: `len(membros) < 2` (os grupos já têm ≥ 2), `PARAGRAPH ≥ 800` (CONTENT já o exige), a guarda `fora` do `aplicar` (defensiva), o filtro FLUXO no ramo da secção (`_seccoes` só devolve caminhos com vocabulário de notícia).

## 5 · Instalação — NÃO FEITA

A condição da missão era «INSTALAR se tudo verde». A suíte do commit novo foi morta pelo Claude Code por falta de memória na máquina. A base `280eb90b` mediu: curadoria 632/632 ok; tests 68 FAIL + 10 ERROR. Sem a comparação, NEW_FAILURES_BY_NAME = NÃO SEI, e não instalei.

Instalar leva também para produção a 6.ª passagem da unificação (SOC2, V1A…), porque o `worker.py` do reparo depende dela. O bot vivo está em `servico-20260923-0923 @ 3d62e87d`.

Plano (padrão B4), quando a suíte der verde:
1. Fotografar processos (supervisor vivo: PID 40520), sha256 dos livros, cópia em `C:\cutover\r1-<hora>\antes`.
2. `PARAR.flag` → o supervisor sai sozinho.
3. Na pasta do bot: `git checkout <R1> --` os `.py` de `curadoria/`, `candidatas/`, `scripts/receitas/`, `scripts/reparo/` que diferem de `3d62e87d`; commit só deles; os livros ficam com o sha256 de antes.
4. Portão de egresso IT → PASS → apagar `PARAR.flag` → `Start-Process powershell -NoExit` com `py curadoria/supervisor.py`.
5. Provar ao vivo: contar READY no livro a cada hora; esperado ≈ +36 em ~2 h de fila.

**DESFAZER:** `PARAR.flag`, repor `antes/`, relançar.
