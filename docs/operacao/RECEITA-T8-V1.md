# RECEITA-T8-V1 — o coletor de sites também em T8, T9 e T12 (D48)

> Rede **fechada** em toda a missão (proxy `127.0.0.1:9`). **Não instalado. A micro NÃO correu.**
> Nada escrito no serviço vivo: os livros vivos foram **copiados** para a bancada só para o plano,
> e a bancada voltou ao Git (conteúdo conferido por `git hash-object`).

| campo | valor |
|---|---|
| decisão | D48 (bot Luciano, delegação do dono, 25/09): registar o coletor de SITES existente em T8/T9/T12, pelo dono único das receitas; mesmas réguas, portão, D38, robots; saúde animal/veterinária fora POR FONTE; provar primeiro na micro das 10 com contrato |
| ramo | `receita-t8-v1` a partir de `integra-onda2-v1` @ `d235c32a` |
| provas | `data/derivados/RECEITA-T8-V1/` |

## 1 · O registo — `pedido/receitas.py:627-678`

Logo a seguir ao registo do YouTube em T8 (`:625`), o mesmo gesto: o executor que **já existe**
(`italia-recorrente` → `coleta/italy_executor.py`) entra em T8, T9 e T12. Não se cria executor,
não se copia régua, não se toca no portão, no D38 nem no robots.

Três escolhas, cada uma com teste:

| escolha | porquê |
|---|---|
| entra **no fim** da lista | o `resolver()` só reordena com filtros declarados, e `fase` é filtro dele: num pedido social os dois empatam e ganha a ORDEM |
| `serve_fases: [""]` — só serve pedido **sem** fase | sem isto o `resolver()` lê «sem `serve_fases`» como «serve todas»: um pedido T9 `fase=posts fonte=…` (do Scrap/comunicação pública) **subia para o de sites**. Apanhado pelo teste `OSocialNaoMuda` antes de acrescentar a linha |
| **sem** `filtros_por_omissao` | nenhuma destas fontes foi colhida ainda por esta porta; sem `--filtro fonte=` não há fonte inventada |

**Testes** (`tests/test_receita_web_t8_t9_t12.py`): antes **FAILED** (4 falhas, 2 erros); depois
**OK 10/10**. Provam: pedido web de T8/T9/T12 → `italy_executor`; pedidos sociais (4 casos) e sem
filtros (T8, T9) → **o mesmo executor de antes**; os outros universos **iguais à fotografia de
antes** (T2, T3, T4, T5, T6, T7, T10); sem fonte por omissão; a micro vê a receita.

**Mutação: 6/6 mortos** — de sites à frente do social · sem `serve_fases` · fonte inventada · só
T8 · T10 apanha a entrada · não corre o `italy_executor`.

**Vizinhos:** os 20 ficheiros de teste que usam as receitas (499 testes): **as mesmas falhas antes
e depois** (1 falha, 10 erros — dívida da base; comparação por nome, `vizinhos-ANTES/DEPOIS.txt`).

## 2 · As 22: produção animal / saúde animal-veterinária / outro

Prova de conteúdo **guardado**, sem rede: páginas do gabarito do detector de capa
(`~/ld2-controlo/bytes`, `~/detector-capa-gabarito/bytes`, fora do Git — sha256 de cada uma em
`animal-22-leitura.txt`) para 10 fontes; para as outras 12, o endereço do item que o Curator abriu
(livro vivo). Contagem de palavras de saúde animal (veterinar, vaccin, malatti, patolog…) contra
produção animal (allevament, zootecn, latte, suini, bovin…).

| classe | fontes | prova |
|---|---|---|
| **PRODUÇÃO ANIMAL** | **IT-T8-030** Informatore Zootecnico | leite, preço do leite, queijo: saúde 0–1 · produção ~70 |
| **PRODUÇÃO ANIMAL, com conteúdo veterinário** | **IT-T8-040** Suinicoltura | revista de criação de porcos (capa: saúde 6 · produção 28), **mas o item do canário é uma vacina** («Coliprotec F4/F18: salute intestinale del suinetto», saúde 18) |
| **SAÚDE ANIMAL / VETERINÁRIA (foco)** | **nenhuma** | — |
| **OUTRO** | as 20 restantes | culturas, máquinas, vinha, fruticultura, horticultura, PAC/PSR, regiões, energia, universidade, feira Didacta |

**Nenhuma fica fora por saúde animal**, porque nenhuma tem esse foco. A **Suinicoltura** é
produção animal (fica dentro, D48), mas vai trazer itens veterinários — e a porta de admissão
**não** filtra veterinária. Registo para decisão: aceitar assim, ou excluir pelo caminho canónico
(a marca `RETIRADA_POR_DECISAO` no contrato do Curator, como a D9 — reversível).

Relevância que não é deste ponto, mas fica escrita: IT-T12-117 (comunidades de energia, Calábria)
e IT-T9-021 (feira Didacta, educação) são de assunto agrícola duvidoso; decide a Admission item a item.

## 3 · A micro nas 10 com contrato — plano (só papel; NÃO correu)

**Efeito no plano** (`micro_coleta.py plano`, sem rede, na bancada com os livros vivos copiados —
sha256 em `livros-vivos-copiados.sha256`; a fila do robô **não** foi copiada, D41.3):

```text
ANTES do registo   prontas 18 · bloqueadas 55 · elegíveis 73
DEPOIS do registo  prontas 28 · bloqueadas 45 · elegíveis 73   (+10, 0 perdidas; painel do portão igual)
```

As 10 novas prontas: IT-T12-137, IT-T8-021, 028, 029, 030, 034, 039, 040, 051, IT-T9-021. As outras
12 das 22 continuam só por `SEM_CONTRATO_DE_COLETA` (bancada CONTRATO-44).

**⚠️ O teto D38 conta por DOMÍNIO, não por site** (`coleta/italy_pilot_collect.mjs:516`,
`dominioRegistavel`; D38: «máx. 5 pedidos por domínio por corrida, incluindo o índice, somando fontes
do mesmo domínio»). **8 das 10 são `edagricole.it`** (terraevita ×2, rivistafrutticoltura,
contoterzista, informatorezootecnico, macchineagricolenews, rivistaorticoltura, suinicoltura). Numa
corrida só, as 8 dividem **5 pedidos**: índice + 1 alvo = 2 por fonte → **~2 fontes Edagricole por
corrida**. (Se o `robots.txt` também conta para o teto: NÃO SEI — não medido; pode ser só 1 fonte.)

**Plano proposto:**

| corrida | fontes | pedidos por domínio |
|---|---|---|
| 1 | IT-T12-137 (psrn.it) · IT-T9-021 (fieradidacta.indire.it) · IT-T8-021 (terraevita) · IT-T8-030 (informatorezootecnico) | psrn ≤5 · indire ≤5 · edagricole ≤5 (2 fontes) |
| 2 | IT-T8-028 (frutticoltura) · IT-T8-029 (contoterzista) | edagricole ≤5 |
| 3 | IT-T8-034 (macchine agricole) · IT-T8-039 (orticoltura) | edagricole ≤5 |
| 4 | IT-T8-040 (suinicoltura) · IT-T8-051 (terraevita) | edagricole ≤5 |

Critério para ampliar (D48): cada fonte com RAW + DERIVED gravados, C4 sem proveniência partida, e
o medidor A da trava (`trava-medidores-v1`) a vê-la sair de `NAO_SEI` a partir do registo da onda em
`ferramentas/big_collection/`. Só depois as 12 sem contrato.

## 4 · Mapa e instalação

Mapa: **espera** — `LOCK-PRIORIDADE.txt` existe (INTEGRA-ONDA2) e a regra pede LOCK-PESADO livre e
≥ 5 GB. Quando correr, fica aqui o SHA e «PRONTO PARA INSTALAR».

## Em palavras simples

- O coletor de sites passou a valer também para três grupos que só tinham o de redes sociais. Um
  pedido de rede social continua a ir para o mesmo sítio de antes — isso está testado.
- Com isso, as fontes prontas passam de **18 para 28**.
- Nenhuma das 22 é de saúde animal como assunto principal. Uma revista de criação de porcos traz
  às vezes páginas de vacinas — fica anotado para decidir.
- 8 das 10 são da mesma editora, e o limite de 5 pedidos vale para a editora inteira. Por isso a
  prova tem de ser feita em 4 noites, 2 revistas de cada vez.
