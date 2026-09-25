# REROUTE D2 (D56) — a Admissão pergunta às outras gavetas

Ramo `reroute-d2-v1`, a partir da produção `df0865e6`, com `ajustes-micro-v1` junto (parte 4).
**Rede fechada, nenhum pedido.** O vivo e a Sala não foram tocados. Os textos e os livros foram lidos de
**cópias**, com sha256 em `INSUMOS-REROUTE.txt`.

## 1. O que mudou na Admissão (dono único da decisão)

- **`admissao/admissao.py:1513` `reencaminhar(item, origem)`:** faz a mesma pergunta do tema
  (`_do_universo`, com a régua de cada gaveta tal como está) a todas as gavetas com régua
  (`PERGUNTAS_DO_UNIVERSO`: T1, T10, T2, T3, T4, T5, T7, T9), menos a da fonte. Devolve `ORIGEM`,
  `UNIVERSE_MATCH=NO`, `SINTONIA_RELEVANT` (YES se houver destino, senão NAO_SEI), `ACTION` e
  `DESTINOS = [{UNIVERSO, PONTUACAO, MOTIVO}]`. A pontuação são os sinais que a régua contou; os
  destinos vão por pontuação e, no empate, pelo universo.
- **`admissao/admissao.py:1579`:** em `decidir()`, quando a gaveta da fonte diz **NÃO ou NÃO_SE_APLICA**
  na pergunta do tema, o REROUTE fica na **evidência** da decisão.
  - O **veredito da gaveta da fonte não muda** e a decisão continua a ser dessa gaveta.
  - NÃO SEI e SIM não reencaminham.
  - Os portões do estágio (legível, origem, identidade, quarentena capa/matéria) já passaram e não se repetem.
  - Uma capa (NÃO na pergunta «matéria») **não** é reencaminhada: não é pergunta de tema.
- **Nenhuma régua mudou.** Nenhum caminho novo pousa na Sala (ver 2).

## 2. A Sala — PARADO: precisa de migração (decisão à parte)

**Hoje não há como ligar UM item a várias gavetas sem duplicar:**
- `supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql:147-148`: cada linha tem **um**
  `universo text not null` e o **texto inteiro** (`texto text not null`); chave `(run_id, ordem)` (`:177`).
- `admissao/sala_de_espera.py:683`: a identidade é `(item_id, universo)`, e o comentário já prevê o
  REROUTE. Mas o único jeito de o fazer hoje é **uma segunda linha com o mesmo texto**, o que duplica o
  conteúdo, e a D56 proíbe.
- Quem pousa: `orquestrador/orquestrador.py:654` (só `d.resultado == SIM`) → `pronto_para_inteligencia`
  (`admissao/admissao.py:1860`) → `sala_de_espera.pousar` (`:907`). O mesmo em
  `coleta/rota_forward_documento.py:346`.

**Proposta de migração 033** (não criada nem aplicada; é decisão do dono da Sala):

```sql
-- 033_o_item_mora_em_varias_gavetas.sql  (PROPOSTA)
create table if not exists public.sala_de_espera_gaveta (
  run_id      text    not null,
  ordem       integer not null,
  universo    text    not null,                     -- a gaveta onde o item TAMBEM mora
  origem      text    not null,                     -- a gaveta da fonte (a que disse NAO)
  pontuacao   integer not null check (pontuacao > 0),
  motivo      text    not null,                     -- as palavras da regua do destino
  decidido_em timestamptz not null default now(),
  primary key (run_id, ordem, universo),
  foreign key (run_id, ordem) references public.sala_de_espera (run_id, ordem),
  check (universo <> origem)
);
```

- O item **mora uma vez** em `sala_de_espera`, com o texto e a proveniência, na gaveta do melhor destino.
  Cada gaveta extra aprovada é **uma linha fina** em `sala_de_espera_gaveta`: sem texto e sem bytes.
- A Inteligência passa a ler «os itens da gaveta X» como
  `sala_de_espera.universo = X UNION sala_de_espera_gaveta.universo = X`.
- Falta decidir o **pouso**: hoje `pousar` só recebe SIM da gaveta da fonte. Depois da 033, um NÃO com
  REROUTE pousa **uma** linha (melhor destino) mais as linhas finas dos outros destinos.

## 3. Medição antes/depois no acervo completo (`MEDICAO-REROUTE-V1.json`)

**Corpus:** 1.358 textos únicos, isto é, os 1.309 do gabarito das réguas mais os **49 documentos das
ondas de hoje** (16 do MICRO-V3 e 33 da 2.ª onda).
- Os 49 foram ligados ao livro de decisões **pela ordem**, e a ligação foi verificada: **49/49**
  rejulgados na gaveta declarada dão exatamente o veredito do livro.
- O armazém da Sala foi lido por **cópia** (782 textos).

| Pergunta | Resultado |
|---|---|
| **Nenhuma régua muda?** 10.864 julgamentos (1.358 × 8 gavetas), base `df0865e6` contra este ramo | **SIM: 0 vereditos mudaram** |
| Textos com gaveta declarada conhecida (gabarito pelo sha do texto + os 49) | 450 |
| … que dizem NÃO/NÃO_SE_APLICA na gaveta da fonte (pergunta do tema) | 275 |
| **… que passam a ter SIM noutra gaveta** | **124** |
| Por origem | T12 64 · T2 49 · T10 4 · T7 3 · T3 2 · T5 2 |
| Por destino (um item pode ter vários) | **T5 106 · T9 35 · T4 35** · T7 9 · T3 5 · T2 5 · T1 3 · T10 2 |

### ⚠️ Contra os rótulos HUMANOS (gabarito V1: `SINTONIA_RELEVANT`)

Dos 248 textos rotulados que dizem NÃO na gaveta da fonte:

| O humano disse | REROUTE acende (SIM) | REROUTE não acende |
|---|---|---|
| **serve ao Sintonia (YES)** | 8 | 5 |
| **não serve (NO)** | **94** | 63 |
| não sei | 4 | 74 |

**Precisão ≈ 8 % (8 em 102 acesos); recall 62 % (8 em 13).**

- Os destinos que acendem são quase todos **T5, T9 e T4**. São as réguas antigas, de palavras soltas
  («revista», «ricerca», «evento», «prodotto»…), que casam com o **menu** dos sites.
- Só com T1/T2 como destino (as réguas D29 medidas em gabarito), a precisão fica sem falsos, mas o
  recall cai a **0** (nenhum dos 13 úteis).

### Leitura à mão (10)

| # | Texto | Destino | Humano | Leitura |
|---|---|---|---|---|
| 1 | Plantgest: vinha integrada × biológica (ensaio de Geisenheim) | T5 | — | **certo** |
| 2 | Plantgest: geada, previsão da gelada radiativa | T2 (1.º), T5, T9, T1 | — | **certo** (T2 é a gaveta) |
| 3 | ARPA Marche: evento institucional em Pesaro | T5 | — | **errado** |
| 4 | ARPA Marche: SIN de Falconara (ambiente e saúde) | T5 | — | **errado** |
| 5 | ERSAF: formação e dias demonstrativos | T5 (1.º), T9 | YES | **parcial**: serve, mas a gaveta certa seria T9, não T5 |
| 6 | CIA Toscana: comunicados de imprensa | T9 | YES | **parcial**: serve; T9 duvidoso |
| 7 | IRET: linhas de pesquisa | T5 | YES | **certo** |
| 8 | CIA: página inicial | T9, T5 | NO | **errado** |
| 9 | ARPA Marche: Falconara (outra captura) | T5 | NO | **errado** |
| 10 | Região: «bollo auto e tributi» | T5, com pontuação 5 | NO | **errado**: o menu acende o T5 |

**Resultado: 3 certos, 2 parciais, 5 errados.**

**Conclusão honesta:** a D56 está implementada como pedida («perguntar às outras gavetas com régua,
nenhuma régua muda») e fica **registada no livro**. **Pousar esses SIM na Sala hoje meteria cerca de 11
itens errados por cada certo.** O defeito não é o REROUTE: são as réguas T4, T5 e T9, que nunca foram
medidas contra gabarito e casam com menus.

**Recomendação:** antes de ligar o pouso (e a 033), exigir que a régua do destino tenha precisão medida
em gabarito. Hoje só T1 e T2 (D29) a têm, e elas não acendem nenhum dos úteis. Ou seja: **medir T5,
T9 e T4 com gabarito é o próximo passo, não o pouso.**

## 4. Preparado para instalar: `entrada_final.py` (AJUSTES-MICRO)

Junta `origin/ajustes-micro-v1` sem conflito: `curadoria/entrada_final.py`,
`ferramentas/rendimento/medir_saltos.py`, os testes e a fixture.

**Passos, com o bot quieto:**
1. `py curadoria/entrada_final.py --saltos=ferramentas/rendimento/ajustes/SALTOS-DA-COORTE.json --contratos=curadoria/italy_contracts_curator.json --observacoes=data/collection-ledger/italy/observations.ndjson --aplicar`
   Muda só a INDEX_URL de IT-T7-021 e IT-T5-160, com PRECISA_DE_REMEDIR.
2. **Teste de rota** das 2, com rede, VPN IT pelo portão de consenso e o teto D38:
   `py medidas/canario_rotas_elegiveis.py --fontes=IT-T7-021,IT-T5-160 --juntar`.
   A prova nova grava `CONTRATO_SHA256` = o sha novo do contrato.
3. O onboarding do supervisor (PONTE) leva a entrada nova à tabela do coletor, só com a prova igual e
   com no máximo 7 dias.

**Desfazer:** repor `curadoria/italy_contracts_curator.json` a partir da cópia de segurança. No ensaio,
o sha voltou a `42f0d9af`.

## Testes e mutação

- `tests/test_reroute_d2.py` **6/0**. Os testes 3 e 4 corriam «em vazio» (paravam num portão antes do
  tema); foram corrigidos e agora falham se não chegarem à pergunta do tema.
- `provas/reroute_mutacao.py` **7/7 mortos** (`provas/REROUTE-MUTACAO.json`): sem REROUTE, troca de
  universo, duplica bytes, NÃO SEI reencaminha, origem nos destinos, destino sem SIM, e o REROUTE a
  mudar o veredito.
- `tests/test_entrada_final.py` **6/0** (da AJUSTES-MICRO).
