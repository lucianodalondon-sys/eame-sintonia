# REROUTE-D56 — um documento, todas as réguas, um item com várias gavetas

Ramo `claude/reroute-d56-admission-gjuys1`, base `a2aa73f4` (= `origin/servico-20260923-0923`, LOTE 8), 28/09/2026.
Offline: sem rede, sem a Sala real, sem livros vivos escritos. **Nada foi ligado no vivo.**

> D56 (bot Luciano, 25/09 09:05), verbatim: «B + (i): implementar o REROUTE na Admissão para todas as
> fontes; se o item der SIM em vários universos, UM item canónico ligado a TODAS as gavetas aprovadas (sem
> duplicar bytes nem proveniência), com pontuação e motivo de cada decisão.»

```
LIVRO (236 pares documento×pedido com texto, 193 documentos)   itens na Sala 19 → 25 · gavetas 19 → 37
ACERVO INTEIRO (hipótese: pedido = território da fonte)        itens na Sala 38 → 40 · gavetas 38 → 51
SIM PERDIDOS                                                   0
NOVOS SIM LIDOS                                                40 (≥ 30) · rótulo de modelo, VALIDADO_POR_HUMANO = NÃO
PRECISÃO (todas as réguas a promover)                          20/32 = 62,5 % (estrita) · 71,9 % (larga)
PRECISÃO (o que promove hoje: T1 T2 T3 T10)                    18/18 no livro · 20/20 com o acervo — DENTRO da amostra
TESTES test_reroute_d56                                        22/22 (5 contra Postgres 16 descartável)
MUTAÇÃO                                                        20/20 mortos (1.ª volta 18/20 → testes apertados)
BATERIA POR NOME                                               ver §6
```

---

## 1 · O que mudou na porta (`admissao/admissao.py`)

**`decidir()` não mudou.** O par (item, universo do PEDIDO) é julgado byte a byte como antes e fica no livro
com `evidencia.d56.papel = "PEDIDO"`. O que é novo vive num bloco só (`admissao/admissao.py:1589` em diante):

| peça | o que faz | onde |
|---|---|---|
| `decidir_todas(item, pedido)` | a decisão do pedido + **uma por cada outro universo do Atlas** (`leis/territorios.CANONICOS`, T1…T12). Só pergunta a mais quem passou **todos** os portões de prontidão do seu estágio (legível, origem, linhagem, identidade, matéria): o portão é do ITEM, não do universo | `admissao.py:1831` |
| `julgar_reroute(item, U)` | a **mesma régua** de `_do_universo`, mais apertada (abaixo). Universo sem régua (T6, T8, T11, T12) → `NAO_SE_APLICA` **só para ele** | `admissao.py:1785` |
| `principal(decisões)` | a gaveta da LINHA: o pedido, se deu SIM; senão a SIM de maior pontuação (empate: ordem do Atlas) | `admissao.py:1865` |
| `gavetas_para_a_sala(decisões)` | **todas** as gavetas aprovadas, a da linha primeiro: `{UNIVERSO, PONTUACAO, MOTIVO}` (motivo = regra, versão, pedido, motivo e 1.º trecho) | `admissao.py:1880` |
| `REROUTE_ENTRA_NA_SALA = True` | a chave. `False` = o livro anota tudo e a Sala só recebe o pedido, como antes (D66) | `admissao.py:1653` |

Cada par (item, universo) tem **decisão, regra (`reroute D56`), motivo, pontuação e trecho**, e vai para o
livro — SIM ou não (D61–D64: nunca se descarta por faltar dado).

### A régua do reroute é a mesma, mais apertada — nunca mais larga

1. **Julga o CORPO, não a página** (`admissao.py:1687`): numa página HTML o texto julgado é
   `leis/fato_do_texto.corpo()` (sem menu, cabeçalho, rodapé nem manchetes vizinhas). Não há extrator novo.
   Corpo < 200 caracteres → `NAO_SEI` (`CORPO_NAO_SEPARAVEL`). A língua mede-se no item inteiro.
2. **Nenhum SIM sem trecho** do texto julgado (`SEM_TRECHO` → `NAO_SEI`).
3. **O termo tem de começar palavra** (`inicio_de_palavra`, `admissao.py:887`): medido neste replay,
   `revista` casava em «p**revista**» e `tesi` em «sin**tesi**» — 3 SIM de T5 só por isso.
4. **T9 pede um concorrente nomeado** (BASF, Bayer, Syngenta, Corteva, FMC, UPL, Nufarm — Atlas — e as empresas
   das fichas IT-T9 009–013/020). Os 28 documentos de cantina que davam T9 ficam `T9_SEM_CONCORRENTE_NOMEADO`.
5. **Só promove quem tem régua medida** (`REROUTE_PROMOVE = {T1, T2, T3, T10}`, `admissao.py:1676`). T4, T5,
   T7, T9 dão `NAO_SEI` com `REROUTE_REGUA_SEM_MEDIDA` — com o trecho no livro, fila seguinte a medir.
   ⚠️ **A exclusão de T4/T5 foi decidida DENTRO desta amostra** (T4 1/6, T5 1/8 lidos).

A pergunta do PEDIDO não ganhou nenhum destes apertos (mudar a régua do pedido é outra decisão —
PORTA-DA-SALA-RENDE §5).

### A estrada (`orquestrador/orquestrador.py:771`)

`pela_porta` chama `decidir_todas`, escreve **todas** as decisões no livro, pousa **um READY por item**
(`principal`) e passa as gavetas ao `pousar`. O recibo de sempre (`por_resultado`) continua a contar só o
pedido; o novo bloco `REROUTE` diz por universo, quantos itens entraram só por reroute e quantas gavetas
novas pousaram.

## 2 · O contrato da Sala — sem quebrar quem lê

- **O READY não mudou** (mesmos 24 campos, mesma ordem, mesma impressão da corrida). `UNIVERSO` continua a
  ser a gaveta da LINHA.
- **As outras gavetas** pousam em `sala_de_espera_gaveta` — a tabela **já existia** (033, secção C, vazia
  por D66) — na **mesma transação** do `pousar` (`sala_de_espera.py:960`). Sem texto, sem bytes, sem
  proveniência, sem `document_key`: só `(run_id, ordem)` da linha, `universo`, `origem`, `pontuacao`, `motivo`.
- **O universo saiu da identidade** (`sala_de_espera.py:870`): o mesmo item/documento noutro universo **já
  não ganha 2.ª linha** — o universo dele vira gaveta da linha que lá está. A mesma gaveta outra vez não
  escreve nada (retry e corrida nova incluídos).
- **`sala_de_espera_atual` não mudou.** A migração nova é **só uma vista**:
  `supabase/migrations/038_a_sala_mostra_cada_item_em_cada_gaveta.sql` → `sala_de_espera_por_gaveta`
  (uma linha por item × gaveta, papel `LINHA` ou `REROUTE`). Desfazer: `supabase/desfazer/038_desfazer.sql`.
  (037 está tomada pela proposta do MAESTRO-SOCIAL.) Provada em Postgres 16 **descartável**: sobe, desce, sobe.
- Leitura: `sala_de_espera.ler_gavetas(run_id)`; backend FICHEIRO guarda-as ao lado (`<run>.gavetas.json`).

⚠️ **Testes desatualizados ajustados, DECLARADO (citando a D56):** `tests/test_sala_idempotente_por_documento.py`
(`test_4`) e `tests/test_sala_dedup_por_document_key.py` (`test_R`) esperavam uma 2.ª LINHA para o mesmo
documento noutro universo («REROUTE D2 = outra entrada»). Agora esperam 0 linhas novas e 1 gaveta.

## 3 · Replay offline (`provas/reroute_d56/`)

`replay_reroute_d56.py` → `REPLAY-REROUTE-D56.json` + `NOVOS-SIM-D56.json`. Lê o livro versionado
(1.243 decisões; 600 sem texto no repositório) e o acervo versionado (páginas HTML + textos de PDF),
com o carregador da PORTA-DA-SALA-RENDE. A Sala do replay tem um item por documento.

### 3a · Itens na Sala por universo — os pedidos que o livro fez

| universo | ANTES (pedido) | DEPOIS (D56) |
|---|---|---|
| T1 | 0 | **7** |
| T2 | 0 | **8** |
| T3 | 0 | **3** |
| T5 | 2 | 2 |
| T10 | 17 | 17 |
| **itens** | **19** | **25** (+6, 13 pedidos que só entram por reroute) |
| **gavetas** | 19 | **37** (7 itens com mais de uma) |

Acervo inteiro (hipótese, pedido = território da fonte, 223 documentos): 38 → **40** itens, 38 → **51** gavetas
(T1 0→7, T2 4→10). **SIM perdidos: 0** nos dois.

Porque não é mais (livro, pares perguntados a outros universos): 72 pedidos param no portão `origem`
(PDF com `SOURCE_ID = NAO SEI`) e 19 no `materia` — não são perguntados a mais nada; 17 páginas sem corpo
separável (`CORPO_NAO_SEPARAVEL`); 28 comunicações de cantina sem concorrente (T9); 17 SIM de T4/T5 retidos
por régua sem medida.

### 3b · Os novos SIM, lidos (`leitura_novos_sim.py` → `LEITURA-NOVOS-SIM-D56.json`)

Lidos **40** (32 do livro + 8 só do acervo), cada um pelo trecho do corpo e pelo título/URL, com **todas** as
réguas a promover (antes da regra 5). Rótulo meu (modelo), `VALIDADO_POR_HUMANO = NÃO`.

| universo | verdadeiro | falso | discutível | exemplos de falso |
|---|---|---|---|---|
| T1 | 7 | 0 | 0 | — |
| T2 | 10 | 0 | 0 | — |
| T3 | 3 | 0 | 0 | — |
| T4 | 1 | 6 | 0 | prémio de cantina: «riconosciuto dal Ministero» + «ogni singola etichetta»; DdL do vinagre (política, T12) |
| T5 | 1 | 7 | 4 | «Ministero dell'Istruzione, dell'Università e della Ricerca»; «convegno/rivista» de revista de comércio |
| T7 | 1 | 0 | 0 | — |

**Precisão medida:** todas as réguas 20/32 = **62,5 %** estrita (71,9 % larga); o que promove hoje
(T1 T2 T3 T10) **18/18** no livro, **20/20** com o acervo. ⚠️ Dentro da amostra, n pequeno, e vários são o
mesmo boletim ARPAV em zonas diferentes (documentos distintos, conteúdo quase igual). Exemplos verdadeiros:
boletins ARPAV/Campania/Puglia/APOL pedidos a T5/T7 — «Fenologia: inolizione – inizio invaiatura», «Soglia
di intervento: 10%…».

⚠️ **Limite:** `corpo()` deixa passar uma linha longa de menu (Terre Etruria: o trecho de T7 começa em
«Contatti Punti Vendita…»). O conteúdo era de T7; o trecho leva menu.

## 4 · Testes (`tests/test_reroute_d56.py`, 22)

SIM em 2 universos = **1 item com 2 gavetas** · NÃO em todos = **0 item** (cantina) · universo sem régua = **NSA
só para ele** (pedido T12 → entra por T3) · **menu não conta** (o mesmo texto lido inteiro daria SIM; no corpo
não) · página sem corpo = NAO_SEI · todo SIM traz trecho com os termos · item parado num portão não é
perguntado a mais nada · `decidir` do pedido igual ao de antes · chave desligada só anota · gaveta mal formada
é recusada · estrada FICHEIRO (1 READY, 1 gaveta, livro com 24 decisões; **reprocessar não duplica**) · reprocesso
seco determinístico e as três travas · **Postgres descartável**: 1 linha + vista com 2 gavetas; retry e outra
corrida não duplicam; documento já na Sala noutro universo ganha a gaveta do pedido; reprocesso da Sala antiga
(idempotente, recusa origem que mudou); 038 só cria a vista, desfaz e sobe.

**Mutação** (`provas/reroute_d56/mutar_reroute_d56.py` → `MUTACAO-REROUTE-D56.json`): **20/20 mortos**. Na
1.ª volta sobreviveram 2 (reroute a casar pedaço de palavra; `--aplicar` sem backup) — os testes foram
**apertados**, não a régua afrouxada.

## 5 · Instalar (NÃO executado — quem instala é o coordenador)

**Ordem:** 038 é só vista; o código escreve em `sala_de_espera_gaveta` (033, já na Sala). A cadeia aplica
tudo o que faltar (034/036 se ainda não estiverem — conferir o livro-razão antes).

```bash
S=$HOME/sintonia-sala-italia
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH" PGPASSFILE="$S/pgpass.conf"
DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"; B=/c/inst/$(date +%Y%m%d-%H%M)-reroute-d56; mkdir -p $B

# 0 · robô parado (o mesmo interruptor da coleta contínua)
echo "REROUTE-D56 a instalar" > curadoria/PARAR.flag

# 1 · backup PROVADO (restaurado numa cópia e comparado) — tem de dar PROVA_VALE=true
py scripts/micro_coleta/provar_backup_da_sala.py --saida=$B

# 2 · código do ramo no vivo (merge para a linha de serviço) e a 038 pela cadeia
bash motor/cadeia_canonica.sh migrations "$DSN" | tee $B/up.txt      # 038 = PASS; as já aplicadas SKIP
bash motor/cadeia_canonica.sh migrations "$DSN" | tee $B/up2.txt     # idempotente: 038 SKIP HASH=MATCH

# 3 · reprocessar a Sala que já existe — SECO por omissão (não escreve nada)
export SINTONIA_SALA_BACKEND=POSTGRES SINTONIA_SALA_DSN="$DSN"
py admissao/reprocessar_reroute.py --exportar $B/copia.json            # só lê a Sala
py admissao/reprocessar_reroute.py --entrada $B/copia.json --saida $B/plano.json
#    ler o plano: GAVETAS_NOVAS, GAVETAS_POR_UNIVERSO, DUPLICADOS_ANTES_DA_D56 (ficam: nunca se apagam)

# 4 · aplicar — recusa sem PROVA_VALE, sem PARAR.flag, ou com código diferente do seco
py admissao/reprocessar_reroute.py --aplicar $B/plano.json --backup $B/PROVA-BACKUP-SALA.json --recibo $B/recibo.json
py admissao/reprocessar_reroute.py --aplicar $B/plano.json --backup $B/PROVA-BACKUP-SALA.json   # 2.ª vez: INSERIDAS 0

# 5 · religar o robô
rm curadoria/PARAR.flag
```

**Desfazer:** `psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/038_desfazer.sql "$DSN"`
(só a vista). As gavetas escritas ficam (a tabela é da 033); caminho completo: `pg_restore` do dump do passo 1.
Código: `REROUTE_ENTRA_NA_SALA = False` (volta a só anotar) ou `git revert`.

## 6 · Provas

- Bateria por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada, Postgres descartável disponível):
  ver `provas/reroute_d56/BATERIA-*.json` e o relatório final da missão.
- System Map: `correr_a_cadeia.py REGERAR` + `VALIDAR` → `SYSTEM_MAP_CHECK=PASS`;
  `impressao_da_arvore.py --conferir-carimbo` → `IGUAL` (depois do commit). Peças declaradas: `C-ADMISSAO`,
  `C-SALA-DE-ESPERA` (+ `admissao/reprocessar_reroute.py`), `C-PROVA-COLETA` (+ `provas/reroute_d56/*`).
  **Não recarimbei** (`--stamp`): as descrições foram acrescentadas, a releitura humana é de gente.

## 7 · O que fica para decisão (bot Luciano / dono)

1. **D66 × D56:** a 033 cita a D66 («o REROUTE só anota»). Esta missão mandou a D56. A chave está à vista
   (`REROUTE_ENTRA_NA_SALA`); no ramo está `True`.
2. **T4 e T5 no reroute:** medir com gabarito (ou lista de âncoras de registo/ciência) antes de promover.
   17 SIM retidos no livro, com trecho, esperam essa medida.
3. **As outras rotas que chamam `decidir` só pelo pedido** (`coleta/rota_forward_documento.py`,
   `coleta/linha_busca.py`, `coleta/it/edicoes_do_registro.py`, `coleta/golden_path_pdf.py`) — não foram
   mudadas. Se alguma alimenta a Sala real, NÃO SEI daqui.
4. **Linhagem:** 72 pedidos do livro param no portão `origem` (PDF sem `SOURCE_ID`) — nenhuma régua os recupera.

## EM PALAVRAS SIMPLES

Até hoje cada documento só era perguntado à gaveta do pedido: um boletim de pragas pedido como «rede técnica»
ouvia «não» e ia embora. Agora a porta pergunta a **todas** as gavetas. Se o documento serve para duas, entra
**uma vez só**, com as duas etiquetas — sem copiar o texto nem a origem. Para não encher a Sala de lixo, a
pergunta extra lê só o texto da notícia (não o menu do site), exige a frase que prova, e só aceita as gavetas
cuja régua já foi medida (clima, pragas, cultura, mercado). No livro que temos, a Sala passa de 19 para 25
itens e de 19 para 37 etiquetas; os 18 novos que entram foram lidos e estão certos. As gavetas de regulatório
e ciência davam muito falso (uma cantina premiada «reconhecida pelo Ministério») — ficam anotadas, à espera de
medida. Nada foi ligado na Sala real: o manual está no §5.
