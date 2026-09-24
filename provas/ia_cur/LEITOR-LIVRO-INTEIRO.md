# D32 (0) · O conserto do leitor do canário, medido no livro inteiro (cópia do vivo)

Medido em 24/09/2026, cópia `C:/cur/leitor/copia` (HEAD do ramo + contratos vivos + portão de
consenso). O MESMO canário corre duas vezes por fonte — leitor ANTIGO (literal, antes de 5239309a) e
NOVO (5fef7956) — sobre os MESMOS bytes (cada página buscada uma vez). Egresso IT pelo portão de
consenso de 25 em 25 pedidos; robots pela porta do robô; 2 s por anfitrião. Dados:
`LEITOR-LIVRO-INTEIRO.jsonl` (uma linha por fonte); script `medir_leitor.py`. NÃO instalado.

| medida | fontes |
|---|---:|
| fontes HTML com INDEX_URL + LINK_PATTERN medidas | **650** (548 do livro do robô + 102 da tabela do coletor) |
| entrada não abriu (sem bytes para comparar) | 28 |
| o leitor novo vê MAIS endereços na entrada | 245 (+2 250 endereços no total) |
| o leitor novo vê MENOS endereços | 28 (−38 no total, 1–2 por fonte; causa provável, NÃO medida: duplicados que só diferiam em `&amp;`) |
| **itens (alvos que casam o padrão) 0 → N** | **3** (IT-T5-027 0→1, IT-T5-052 0→17, IT-T7-044 0→10) |
| itens N → 0 | 0 |
| **mudam de veredito** | **2** |
| · IT-T7-044 (ANBI) | SOURCE_FAILURE → PASS DETAIL/v1 (item: artigo com 2 431 caracteres, MATERIA_PROVAVEL) |
| · IT-T1-011 (Regione Umbria) | PASS LEGACY → PASS DETAIL/v1 (1 → 6 alvos; abre outro item, MATERIA_PROVAVEL) |
| **PASS novo cujo item é navegação** | **0** |
| PASS perdidos | 0 |
| exceções | 0 (o link malformado «http://[x» foi consertado antes: 5fef7956) |
| mesmo veredito, outro item aberto | 1 (IT-T2-024: outro PDF; continua a falhar) |
| veredito total ANTIGO → NOVO | PASS 113 → 114 (DETAIL/v1 78 → 80; LEGACY 35 → 34) |

As 2 fontes 0→N que não passaram (IT-T5-027, IT-T5-052) continuam SOURCE_FAILURE: o item que agora
se vê é CAPA_PROVAVEL — o gate de capa apanha-as, como deve.

**Leitura:** o conserto quase não muda vereditos (2 em 650), não faz nenhuma fonte perder o PASS e
não faz nenhuma passar com navegação. O que muda muito é o que o leitor VÊ na entrada (245 fontes),
e isso é o que a R1 (reparo) usa para inferir padrões — o efeito na R1 não está medido aqui.
