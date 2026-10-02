# TEXTO QUE VAI AO OPUS — RELATÓRIO DA MISSÃO (camada de texto do FAST)

`claude/scrap-texto-limpo-v1` · base `6de307bd8`

## 1. O que mudou

Duas coisas, ambas dentro do extrator que já existia (`motor/fast_auto/passo1_selecionar.py`) — **não foi criado extrator paralelo**:

1. **Limpeza do texto, em duas camadas:**
   - **estrutura** — sai o texto que vem de `<nav> <header> <footer> <form> <aside> <button> <select> <label> <input>` e de container cujo `class`/`id` traz um **token inteiro** de casca (`menu`, `menu-item`, `breadcrumb`, `cookie`, `sidebar`, `widget`, `related`, `newsletter`, `login`, `sponsor`, …);
   - **repetição** — sai a linha **curta (≤ 80 chars) que aparece em 3 ou mais documentos da mesma rodada** (menu, rodapé, aviso de cookies, “conta ou e-mail”, “senha esquecida”).
   - **guarda** — se a limpeza derrubar o texto abaixo de 15% do bruto (documento > 2000 chars) **e** a prosa tiver morrido (< 400 chars em linhas de 80+), o BRUTO é entregue e o motivo fica gravado (`LIMPEZA_SUSPEITA_MANTIDO_BRUTO`). Nunca corta o corpo em silêncio.
2. **Hash do texto** — `TEXTO_SHA256` passa a ser o sha256 **do que foi gravado e lido de volta do disco** (prova em `TEXTO_SHA256_NO_DISCO`, 20/20 iguais). O limite de entrega tem **um dono só** (`LIMITE_ENTREGA_CHARS`, no passo1) e o passo2 grava `TEXTO_ENTREGUE_SHA256` / `TEXTO_ENTREGUE_CHARS` / `TEXTO_CORTADO_EM`: **o hash descreve o que o modelo viu**. O `TRECHO` passa a ser conferido **no texto entregue**, não no texto que o modelo nunca viu.

Dois defeitos de encanamento medidos durante a missão e corrigidos:
- `class` de wrapper com `navigation` (tema WordPress) marcava a página inteira como casca — derrubou um documento de 9323 para **24 caracteres**. Token removido da lista; teste de contraprova acrescentado.
- `<head>`/`<title>` sem fecho deixava o corpo inteiro fora, **em silêncio**. `<body>` agora reinicia o estado de skip.

## 2. A prova

| prova | comando | resultado |
|---|---|---|
| antes/depois nos 20 HTML reais da rodada | `provas/antes_depois_do_texto_fast.py` | **137 050 → 69 923 chars; 49,0% a menos; 0 alarmes** |
| hash do texto = hash do ficheiro | rodada de ensaio (banco real, 20 RAW) | **20/20** |
| hash do entregue + corte | `provas/red_team_hash_do_entregue.py` (stub, custo 0) | **20/20**, trecho de dentro → ACEITO, trecho de fora → REJEITADO |
| testes | `pytest tests/test_fast_texto_limpo.py tests/test_fast_auto_rodada.py tests/test_fast_cruzamento_comercial.py` | **26 passam** |

O corpo sobreviveu: nos três documentos onde mais saiu, a matéria continua inteira
(`RAW-2612` “Lo dicono i risicoltori…”, `RAW-2620` “I modelli ad ancore ricurve…”, `RAW-2652` “In corso monitoraggio diossine…”).

## 3. O que NÃO mudou

- contrato do Casco, `CRUZAMENTO-COMERCIAL.json`, seleção de fontes, catálogo, bulas, janelas;
- o rótulo `TRECHO_ENCONTRADO_NO_RAW` (filtrado por `passo3_cruzar.py` e `fast_cruzamento_comercial.py`) — mudá-lo é contrato de outra peça;
- nenhuma chamada ao modelo no caminho novo (o passo2 continua igual, só mede o que entrega).

## 4. O que continua desconhecido / risco

- **lixo residual** dentro do corpo: linha longa de rodapé (“Sede legale Via Eritrea 21…”) e caixa de login do tema (“Accedi”, “Password dimenticata?”) que a regra de estrutura não pega. Medido, não resolvido.
- a camada de repetição depende da rodada: **1 documento por rodada não tem template para comparar**.
- `TEXTO_SHA256_NO_DISCO` e `CONFERE_COM_DOCUMENTOS` contam bytes do ficheiro; o texto entregue é a *string* — documentos com `\r` solto podem diferir entre os dois planos (medido em 3 de 20 antes da correção).
- **INCIDENTE REGISTRADO:** a primeira tentativa de stub do modelo usou `PATH`, mas `shutil.which("claude")` resolveu para o CLI real — o passo2 correu com o modelo real por até 180 s antes do timeout. Não houve artefacto escrito e o ensaio foi refeito com stub em processo (custo 0). Gasto possível **NÃO MEDIDO**.

## 5. KNOW_HOW_DELTA

`ATUALIZAÇÃO NECESSÁRIA` — a regra de limpeza do texto do FAST (duas camadas, token inteiro em vez de substring, guarda por prosa, hash no ponto de entrega) é conhecimento durável e ainda não está no know-how canónico.

## 6. Próximo passo mínimo

Ligar o passo1/passo2 novos na rodada automática da Intelligence e observar: os campos `MARCA_TEXTUAL`, `FORA_POR_REPETICAO_CHARS` e `TEXTO_ENTREGUE_SHA256` passam a aparecer no `FACTS_FAST.json` de cada rodada. O primeiro documento que cair em `LIMPEZA_SUSPEITA_MANTIDO_BRUTO` é um achado a investigar, não um erro.

**HARD STOP.**
